import sys
import os
import shutil
import tempfile

from configparser import ConfigParser
from datetime import datetime

import drivesvc

BACKUP_CONFIG = 'backup.cfg'
LOCAL_DIR = 'Drive_Backup'
DRIVE_DIR = 'PC_Backup'
DRIVE_DIR_ID = ''
COPY_DIR_ID = ''
FILE_PATH = os.path.dirname(os.path.realpath(__file__))


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


def get_dir_ids():
    global DRIVE_DIR_ID
    global COPY_DIR_ID

    config_path = os.path.abspath(os.path.join(FILE_PATH, BACKUP_CONFIG))

    config = ConfigParser()
    config.read(config_path)

    DRIVE_DIR_ID = config.get('drive', 'drive_dir_id')
    COPY_DIR_ID = config.get('drive', 'copy_dir_id')
    LOCAL_DIR = config.get('drive', 'local_dir')
    DRIVE_DIR = config.get('drive', 'drive_dir')
    DRIVE_COPY_DIR = config.get('drive', 'drive_copy_dir')

    if not LOCAL_DIR or not DRIVE_DIR or not DRIVE_COPY_DIR:
      print("Config missing values. Please set")
      exit()

    if not DRIVE_DIR_ID:
      print("Getting Drive directory ID.")

      DRIVE_DIR_ID = drivesvc.get_drive_id()
    
      print("Setting Drive id: %s" % DRIVE_DIR_ID)
      config.set('drive', 'drive_dir_id', DRIVE_DIR_ID)
      config.write(open(config_path, 'w'))

    return (DRIVE_DIR_ID, COPY_DIR_ID)

def remove_copies(copied_file_path):
    for f in os.listdir(copied_file_path):
        os.remove(f)


if __name__ == "__main__":
    print("Manage.py is a module and is not configured as a stand-alone script.")
