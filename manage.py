import sys
import os
import shutil

from configparser import ConfigParser
from datetime import datetime


global LOCAL_DIR
global DRIVE_DIR
global DRIVE_DIR_ID

LOCAL_DIR = 'Drive_Backup'
DRIVE_DIR = 'PC_Backup'
DRIVE_DIR_ID = ''


def create_parent_dir(service):
  file_metadata = {
    'name': DRIVE_DIR,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  
  folder = service.files().create(body=file_metadata,
                                  fields='id').execute()
  return folder.get('id')


def copy_file(file_dir):
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
  exit()

def get_drive_files(service, id):
  q = "'%s' in parents" % id
  print(q)

  results = service.files().list(q=q, 
                               pageSize=10, 
                               fields="nextPageToken, files(id, name)").execute()
  items = results.get('files', [])

  return(items)


def get_parent_dir(service, filepath):
  config_path = os.path.abspath(os.path.join(filepath, 'config.ini'))

  config = ConfigParser()
  config.read(config_path)
  parent_dir_id = config.get('drive', 'parent_dir_id')
  DRIVE_DIR_ID = config.get('drive', "parent_dir_id")

  if not parent_dir_id:
    print("Getting parent directory ID.")

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

      parent_dir_id = create_parent_dir(service)

      config.set('drive', 'parent_dir_id', parent_dir_id)
      config.write(open(config_path, 'w'))

    else:
      for file in response.get('files', []):
        id = file.get('id')

        print("Setting parent id: %s" % id)
        config.set('drive', 'parent_dir_id', id)
        config.write(open(config_path, 'w'))

        parent_dir_id = id

  return parent_dir_id


if __name__ == "__main__":
  print("Manage.py is a module and is not configured as a stand-alone script.")
