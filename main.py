from __future__ import print_function
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from mimetypes import MimeTypes
from manage import get_drive_id, get_drive_files, copy_files, remove_tmp_dir

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
  file_path = os.path.dirname(os.path.realpath(__file__))
  token_path = os.path.abspath(os.path.join(file_path, 'files\\', 'token.json'))

  user = os.getlogin()
  
  # Refactor into get_creds method
  creds = None

  if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)

    with open(token_path, 'w') as token:
      token.write(creds.to_json())

  service = build('drive', 'v3', credentials=creds)

  local_dir = os.path.dirname(r'C:\Users\%s\DriveBackup\\' % user)

  copied_file_path = upload_files(local_dir, file_path, service)

  remove_tmp_dir(copied_file_path)

  print("Completed")


def upload_files(local_dir, file_path, service):
  if os.listdir(local_dir):
    dir_id = get_drive_id(service, file_path)

    copied_files_dir = copy_files(local_dir)
    print(copied_files_dir)

    for f in os.listdir(copied_files_dir):
      print(f)

      mimetype = MimeTypes().guess_type(f)[0]
      file_metadata = {'name': f, 'parents': [dir_id]}
      media = MediaFileUpload(os.path.join(copied_files_dir, f), mimetype=mimetype)

      try:
        service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
      except Exception as ex:
        print("Exception %s " % ex)  

      f = None
    
    return copied_files_dir

  else:
    print("Directory %s is empty." % local_dir)


if __name__ == "__main__":
  main()