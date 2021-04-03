import sys
import os
import shutil
import tempfile

from configparser import ConfigParser
from datetime import datetime

BACKUP_CONFIG = 'backup.cfg'
LOCAL_DIR = 'Drive_Backup'
DRIVE_DIR = 'PC_Backup'
DRIVE_DIR_ID = ''
COPY_DIR_ID = ''

def create_drive_dir(service):
  file_metadata = {
    'name': DRIVE_DIR,
    'mimeType': 'application/vnd.google-apps.folder'
  }
  
  folder = service.files().create(body=file_metadata,
                                  fields='id').execute()
  return folder.get('id')


def copy_files(file_dir):
  # tmp_dir = os.path.join(file_dir, 'tmp')
  # if not os.path.exists(tmp_dir):
  #   os.mkdir(tmp_dir)

  date = datetime.today().strftime('%Y%m%d')
  tmp_dir = tempfile.mkdtemp()
  os.chdir(file_dir)
 
  for f in os.listdir(os.getcwd()):
    if os.path.isfile(f):   
      temp_file = os.path.join(tmp_dir, f)
      
      if not os.path.exists(temp_file):
        shutil.copy(f, temp_file)

  os.chdir(tmp_dir)
  for f in os.listdir(os.getcwd()):
    name, ext = os.path.splitext(f)

    new_name = name + '_' + date + ext
    os.rename(f, new_name)
  
  print("Files copied")
  
  return tmp_dir

def get_drive_files(service):
  q = "'%s' in parents" % DRIVE_DIR_ID
  print(q)

  results = service.files().list(q=q, 
                               pageSize=10, 
                               fields="nextPageToken, files(id)").execute()
  items = results.get('files')

  files_list = []
  for i in items:
    id = i.get('id')
    files_list.append(id)

  return(files_list)


def get_drive_ids(service, filepath):
  global DRIVE_DIR_ID
  global COPY_DIR_ID

  config_path = os.path.abspath(os.path.join(filepath, BACKUP_CONFIG))

  config = ConfigParser()
  config.read(config_path)

  DRIVE_DIR_ID = config.get('drive', 'drive_dir_id')
  COPY_DIR_ID = config.get('drive', 'copy_dir_id')

  print(DRIVE_DIR_ID, COPY_DIR_ID)

  if not DRIVE_DIR_ID:
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

      DRIVE_DIR_ID = create_drive_dir(service)

      config.set('drive', 'drive_dir_id', DRIVE_DIR_ID)
      config.write(open(config_path, 'w'))

    else:
      for file in response.get('files', []):
        id = file.get('id')

        print("Setting Drive id: %s" % id)
        config.set('drive', 'drive_dir_id', id)
        config.write(open(config_path, 'w'))

        DRIVE_DIR_ID = id

  return DRIVE_DIR_ID


def move_drive_files(service, files_in_drive):

  #backup_dir_id = '1GavKxxLmxHEXlgU5foVTfz4RpaxN5BYq'
  for f in files_in_drive:
    if f != COPY_DIR_ID:
      print(f)
      file = service.files().get(fileId=f,
                                 fields='parents').execute()
      previous_parents = ",".join(file.get('parents'))
      # Move the file to the new folder
      file = service.files().update(fileId=f,
                                          addParents=COPY_DIR_ID,
                                          removeParents=previous_parents,
                                          fields='id, parents').execute()


def remove_copies(copied_file_path):
  for f in os.listdir(copied_file_path):
    os.remove(f)

  
if __name__ == "__main__":
  print("Manage.py is a module and is not configured as a stand-alone script.")
