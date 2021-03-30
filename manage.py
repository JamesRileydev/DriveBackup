import sys
import os
from configparser import ConfigParser


def get_parent_dir(service, filepath):
  config_path = os.path.abspath(os.path.join(filepath, 'config.ini'))

  config = ConfigParser()
  config.read(config_path)
  parent_dir_id = config.get('drive', 'parent_dir_id')

  if not parent_dir_id:
    print("Getting parent directory ID.")

    page_token = None

    response = service.files().list(q="name='Backup'",
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken=page_token).execute()

    if not response.get('files', []):
      print("No id found for file")
      create_parent_dir(service)

    else:
      for file in response.get('files', []):
        id = file.get('id')

        print("Setting parent id: %s" % id)
        config.set('drive', 'parent_dir_id', id)
        config.write(open(config_path, 'w'))

        parent_dir_id = id

  return parent_dir_id

def create_parent_dir(service):
  print("Creating parent directory")
  exit()

if __name__ == "__main__":
  print("Manage.py is a module and is not configured as a stand-alone script.")
