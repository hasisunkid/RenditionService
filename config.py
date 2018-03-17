
class Config(object):
    DEBUG = True
    PORT = 5000
    TMP_PATH = 'C:\\Users\\eobs\\python\\converter'
    TMP_FILE_EXPR = 60

    ALLOWED_EXTENSIONS = [{'EXTENTION': 'pdf', 'MimeType': 'application/pdf', 'CanBeConvertedToPdfA': 'true'},
                          {'EXTENTION': 'docx', 'MimeType': 'application/msword', 'CanBeConvertedToPdfA': 'true'},
                          {'EXTENTION': 'jpg', 'MimeType': 'application/jpg', 'CanBeConvertedToPdfA': 'true'}]

    SOFFICE_CON = ['docx']
    NO_CON = ['pdf']
    IMG_CON = ['jpg','jpeg','tiff']
    SWIDS = ['12345', 'abcd']
    SOFFICE_PATH = r'"C:\Program Files\LibreOffice 5\program\soffice.exe"'
    LOG_PATH = 'log'
    LOGGER_NAME = 'rendition_service'

    JOBS = [
        {
            'id': 'cleanup',
            'func': 'RenditionService:cleanupRun',
            'trigger': 'interval',
            'seconds': 20
        }
    ]

    SCHEDULER_API_ENABLED = True

