from __future__ import print_function
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from mimetypes import MimeTypes
from manage import copy_files, remove_copies, get_dir_ids
import drivesvc

FILE_PATH = os.path.dirname(os.path.realpath(__file__))

def main():
  user = os.getlogin()
  drivesvc.create_service(FILE_PATH)

  drive_id, drive_copy_id = get_dir_ids(FILE_PATH)

  files_in_drive = drivesvc.get_drive_file_ids(drive_id)

  print(files_in_drive)

  drivesvc.move_drive_files(files_in_drive, drive_copy_id)

  local_dir = os.path.dirname(r'C:\Users\%s\DriveBackup\\' % user)

  copied_files_dir = copy_files(local_dir)

  drivesvc.upload_files(copied_files_dir, drive_id)

  remove_copies(copied_files_dir)

  print("Completed")


if __name__ == "__main__":
  main()