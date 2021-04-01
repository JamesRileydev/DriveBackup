import sys
import os
import shutil

from configparser import ConfigParser
from datetime import datetime


global LOCAL_DIR
global DRIVE_DIR

LOCAL_DIR = 'Drive_Backup'
DRIVE_DIR = 'PC_Backup'


def create_drive_dir(service):
  file_metadata = {
    'name': DRIVE_DIR,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  
  folder = service.files().create(body=file_metadata,
                                  fields='id').execute()
  return folder.get('id')


def copy_files(file_dir):
  tmp_dir = os.path.join(file_dir, 'tmp')
  if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

  date = datetime.today().strftime('%Y%m%d')

  os.chdir(file_dir)
 
  for f in os.listdir(os.getcwd()):
    if os.path.isfile(f):   
      temp_file = os.path.join(os.getcwd(),'tmp', f)
      
      if not os.path.exists(temp_file):
        shutil.copy(f, temp_file)

  os.chdir(tmp_dir)
  for f in os.listdir(os.getcwd()):
    name, ext = os.path.splitext(f)

    new_name = name + '_' + date + ext
    os.rename(f, new_name)
  
  print("Files copied")
  
  return tmp_dir

def get_drive_files(service, id):
  q = "'%s' in parents" % id
  print(q)

  results = service.files().list(q=q, 
                               pageSize=10, 
                               fields="nextPageToken, files(id, name)").execute()
  items = results.get('files', [])

  return(items)


def get_drive_id(service, filepath):
  config_path = os.path.abspath(os.path.join(filepath, 'config.ini'))

  config = ConfigParser()
  config.read(config_path)
  drive_dir_id = config.get('drive', 'drive_dir_id')

  if not drive_dir_id:
    print("Getting Drive directory ID.")

    page_token = None
    name = "name='%s'" % DRIVE_DIR
    try:
      response = service.files().list(q=name,
                                      spaces='drive',
                                      fields='nextPageToken, files(id, name)',
                                      pageToken=page_token).execute()
    except Exception as ex:
      print("Exception %s " % ex)  

    if not response.get('files', []):
      print("No id found for file, creating directory in Google Drive")

      drive_dir_id = create_drive_dir(service)

      config.set('drive', 'drive_dir_id', drive_dir_id)
      config.write(open(config_path, 'w'))

    else:
      for file in response.get('files', []):
        id = file.get('id')

        print("Setting Drive id: %s" % id)
        config.set('drive', 'drive_dir_id', id)
        config.write(open(config_path, 'w'))

        drive_dir_id = id

  return drive_dir_id


def remove_tmp_dir(copied_file_path):
  if os.path.isdir(copied_file_path):
    os.remove(copied_file_path)

if __name__ == "__main__":
  print("Manage.py is a module and is not configured as a stand-alone script.")
