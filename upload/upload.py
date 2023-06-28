"""
    python library to upload and download the documents on the dropbox.
"""
import dropbox
"""  
    Time is a built-in module in python libraries, it provides time-stamp in this project.
"""
import time
"""
    OS module of python library provides the function to interact with operating system.
"""
import os
"""
    1) config is locally created module to access the directory object config.
    2) 'from config import config' imports the config dictionary object from local config module.
    3) It facilitates the import of various variable configuration created using jinja2 and yaml modules.
"""
from config import config

source_directory_of_files = '/home/hardik/seminar-project/server'
dropbox_access_token = config['dropbox']['dropbox_access_token']
file_to_be_uploaded = ['statistics.txt', 'summary.json', 'server_data.json', 'server.log','distributions.txt']
dropbox_upload_interval = config['server']['dropbox_upload_interval']
dbx = dropbox.Dropbox(dropbox_access_token)

def uploadFilesToDropbox():
    for file_name in file_to_be_uploaded:
        source_file = os.path.join(source_directory_of_files, file_name)
        target_file = '/' + file_name 
        with open(source_file, 'rb') as f:
            print(f'Uploading {file_name}...')
            dbx.files_upload(f.read(), target_file, mode=dropbox.files.WriteMode('overwrite'))
            print(f'{file_name} uploaded successfully.')
while True:
    uploadFilesToDropbox()
    time.sleep(dropbox_upload_interval)

