# RenditionService

This is just a smal Flask App that offers a Rendition service via Rest API

## Dependdencies

* LibreOffice 
* Python 3.6.x
* Flask
* Img2PDF

## Configuration

Just edit the config.py file
The following parts are importand:

Path for temporary files  
'TMP_PATH = "C:\\...."'  
  
Maximume time a temp file resides 
'TMP_FILE_EXPR = 60' 

Definition of available mimitypes  

'''
  ALLOWED_EXTENSIONS = [{'EXTENTION': 'pdf\', 'MimeType': 'application/pdf', 'CanBeConvertedToPdfA': 'true'},
                          {'EXTENTION': 'docx', 'MimeType': 'application/msword', 'CanBeConvertedToPdfA': 'true'},
                          {'EXTENTION': 'jpg', 'MimeType': 'application/jpg', 'CanBeConvertedToPdfA': 'true'}]
'''

Path to libre office  
'SOFFICE_PATH = r'"C:\Program Files\LibreOffice 5\program\soffice.exe"'

Filetypes for pdf rendering with libre office and images
''' 
SOFFICE_CON = ['docx']
NO_CON = ['pdf']
IMG_CON = ['jpg','jpeg','tiff']
'''

## Running

To Start just type 

'python RenditionService.py'

 

