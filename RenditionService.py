from flask import Flask, request, send_from_directory
from flask import json
from flask import jsonify
from os.path import basename
from flask_apscheduler import APScheduler
import logging
from logging.handlers import RotatingFileHandler
import socket
import img2pdf
import os
import time
import math
import re


# this ist just to initiate the script
app = Flask(__name__)
app.config.from_object('config:Config')

log = app.logger
swids = app.config['SWIDS']

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh = RotatingFileHandler('{0}/{1}.log'.format(app.config['LOG_PATH'],
                                              app.config['LOGGER_NAME']),
                         maxBytes=10000, backupCount=4)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)


log.addHandler(fh)
# log.addHandler(cons)
log.info("Start")
scheduler = APScheduler()


# end of initiation


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.route('/v1/PdfAConverterSupportedMimeTypes', methods=['GET'])
def getSupportetMomeTypes():

    log.info("get info")
    response = app.response_class(
        response=json.dumps(app.config['ALLOWED_EXTENSIONS']),
        status=200,
        mimetype='application/json')
    return response


@app.route('/v1/PdfAConverterNodes/<swid>', methods=['GET'])
def getAvailablieNodes(swid):

    if swid in swids:

        response = app.response_class(
            response=json.dumps({'DNSName': socket.gethostname()}),
            status=200,
            mimetype='application/json')
        return response
    else:
        raise InvalidUsage('SWID invalid', status_code=403)


@app.route('/v1/PdfAConverter/<swid>/<ext>/<field>', methods=['POST'])
def convertPDFA(swid, ext, field):
    mime_type_supporteed = False
    for mimeType in app.config['ALLOWED_EXTENSIONS']:
        if mimeType['EXTENTION'] == ext:
            mime_type_supporteed = True

    if not mime_type_supporteed:
        raise InvalidUsage('MimeType not Supported', status_code=415)

    log.info(f'Convert from {ext}')
    time_stamp = math.floor(time.time())
    tmp_filename = f'{time_stamp}.{ext}'
    if swid in swids:
        if 'file' in request.files:
            file = request.files['file']
            file.save(os.path.join(app.config['TMP_PATH'], tmp_filename))

        else:
            raise InvalidUsage('No File was sended', status_code=416)
        if ext in app.config['NO_CON']:
            return send_from_directory(
                os.path.join(app.config['TMP_PATH']),
                tmp_filename)
        elif ext in app.config['SOFFICE_CON']:
            orig_file = os.path.join(app.config['TMP_PATH'], tmp_filename)
            convertSoffice(orig_file)
            new_file = waitforPDFFile(orig_file)
            log.info(f'send new file {new_file}')
            return send_from_directory(app.config['TMP_PATH'], new_file)
        elif ext in app.config['IMG_CON']:
            return send_from_directory(app.config['TMP_PATH'],
                                       convertImage(tmp_filename))

    else:
        log.warn(f'SWID {swid} invalid')
        raise InvalidUsage('SWID invalid', status_code=403)


@app.errorhandler(InvalidUsage)
def handle_invalid_swid(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def waitforPDFFile(filename):
    timeout_counter = 0
    new_filename = os.path.splitext(basename(filename))[0] + '.pdf'
    pdfFile = os.path.join(app.config['TMP_PATH'], new_filename)
    log.info(f'waiting for {new_filename}')
    while not os.path.exists(pdfFile):
        time.sleep(1)
        timeout_counter += 1
        if timeout_counter >= 120:
            raise InvalidUsage(
                'cant create rendition timeout', status_code=415)

    return new_filename


def convertSoffice(filename):
    input_file = os.path.join(app.config['TMP_PATH'], filename)
    output_path = app.config['TMP_PATH']
    soffice_path = app.config['SOFFICE_PATH']
    os.system(
        f'{soffice_path} --headless --convert-to pdf --outdir {output_path} {input_file}')


def convertImage(filename):
    new_filename = os.path.splitext(basename(filename))[0] + '.pdf'
    log.info(f'Convert {filename} to {new_filename}')
    pdf_mem = img2pdf.convert(os.path.join(app.config['TMP_PATH'], filename))
    with open(os.path.join(app.config['TMP_PATH'], new_filename), "wb") as f:
        f.write(pdf_mem)
    return new_filename


def cleanupRun():
    tmp_path = app.config['TMP_PATH']
    current_time = math.floor(time.time())
    tmp_file_exp = app.config['TMP_FILE_EXPR']
    log.info("Start Cleanup {tmp_path}")
    for f in os.listdir(tmp_path):
        file_time = int(re.findall('\d+', f)[0])
        file_age = current_time - file_time
        log.debug(f'{f} is {file_age} s old ')
        if file_age >= tmp_file_exp:
            log.info(f'{f} is expired it will deleted')
            os.remove(os.path.join(app.config['TMP_PATH'], f))


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    log.info("start cleanup job")
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=False,threaded=True)
    app.logger.setLevel(logging.DEBUG)
