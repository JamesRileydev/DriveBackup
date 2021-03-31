import sys
import os
from configparser import ConfigParser

global LOCAL_DIR
global DRIVE_DIR

LOCAL_DIR = 'Drive_Backup'
DRIVE_DIR = 'PC_Backup'


def create_parent_dir(service):
  file_metadata = {
    'name': DRIVE_DIR,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  
  folder = service.files().create(body=file_metadata,
                                  fields='id').execute()
  return folder.get('id')


def copy_file():
  print("Copy file called.")


def get_drive_files():
  print("Get drive files called.")


def get_parent_dir(service, filepath):
  config_path = os.path.abspath(os.path.join(filepath, 'config.ini'))

  config = ConfigParser()
  config.read(config_path)
  parent_dir_id = config.get('drive', 'parent_dir_id')

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
