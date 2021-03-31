import sys
import os
from configparser import ConfigParser

global LOCAL_DIR
global PARENT_DIR

LOCAL_DIR = 'DriveBackup'
PARENT_DIR = 'PC_Backup'

def get_parent_dir(service, filepath):
  config_path = os.path.abspath(os.path.join(filepath, 'config.ini'))

  config = ConfigParser()
  config.read(config_path)
  parent_dir_id = config.get('drive', 'parent_dir_id')

  if not parent_dir_id:
    print("Getting parent directory ID.")

    page_token = None
    name = "name='%s'" % PARENT_DIR
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

def create_parent_dir(service):
  file_metadata = {
    'name': PARENT_DIR,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  
  folder = service.files().create(body=file_metadata,
                                  fields='id').execute()
  return folder.get('id')

if __name__ == "__main__":
  print("Manage.py is a module and is not configured as a stand-alone script.")
