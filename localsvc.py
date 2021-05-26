import logging
import os
import sys
import shutil
import tempfile

from configparser import ConfigParser
from datetime import datetime

import drivesvc

BACKUP_CONFIG = 'backup.cfg'
LOCAL_DIR = ''
DRIVE_DIR = ''
DRIVE_COPY_DIR = ''


def copy_files(file_dir):
    tmp_dir = get_temp_dir()

    date = datetime.today().strftime('%Y%m%d')
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


def get_config_dirs():
    exit("get_config_dirs() called")


def get_dir_ids(file_path):
    config_path = os.path.abspath(os.path.join(file_path, BACKUP_CONFIG))

    config = ConfigParser()
    config.read(config_path)

    LOCAL_DIR = config.get('drive', 'local_dir')
    DRIVE_DIR = config.get('drive', 'drive_dir')
    DRIVE_COPY_DIR = config.get('drive', 'drive_copy_dir')

    if not LOCAL_DIR or not DRIVE_DIR or not DRIVE_COPY_DIR:
        print("Config missing values. Please set.")
        exit()

    drive_dir_id = config.get('drive', 'drive_dir_id')
    drive_copy_dir_id = config.get('drive', 'copy_dir_id')

    if not drive_dir_id:
        print("Getting Drive directory ID.")

        drive_dir_id = drivesvc.get_drive_id(DRIVE_DIR)

        print("Setting Drive id: %s" % drive_dir_id)
        config.set('drive', 'drive_dir_id', drive_dir_id)
        config.write(open(config_path, 'w'))

    if not drive_copy_dir_id:
        print("Getting Drive copy directory ID.")

        drive_copy_dir_id = drivesvc.get_drive_id(DRIVE_COPY_DIR)

        print("Setting Drive Copy id: %s" % drive_copy_dir_id)
        config.set('drive', 'copy_dir_id', drive_copy_dir_id)
        config.write(open(config_path, 'w'))

        drivesvc.move_drive_files([drive_copy_dir_id], drive_dir_id)

    return (drive_dir_id, drive_copy_dir_id)


def get_temp_dir():
    config = ConfigParser()
    config_path = os.path.join(os.path.abspath(os.getcwd()), BACKUP_CONFIG)
    config.read(config_path)

    temp_dir = config.get('drive', 'local_copy_dir')

    if not temp_dir:
        temp_dir = tempfile.mkdtemp()
        config.set('drive', 'local_copy_dir', temp_dir)

        with open(config_path, "w") as file:
            config.write(file)

    return temp_dir


def remove_copies(copied_file_path):
    for f in os.listdir(copied_file_path):
        os.remove(f)


if __name__ == "__main__":
    print("localsvc.py is a module and is not configured as a stand-alone script.")
