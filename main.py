from __future__ import print_function
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from mimetypes import MimeTypes
from manage import get_parent_dir, get_drive_files, copy_file

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
  file_path = os.path.dirname(os.path.realpath(__file__))
  token_path = os.path.abspath(os.path.join(file_path, 'files\\', 'token.json'))

  user = os.getlogin()

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

  file_dir = os.path.dirname(r'C:\Users\%s\DriveBackup\\' % user)
  
  upload_files(file_dir, file_path, service)

  print("Completed")


def upload_files(file_dir, file_path, service):
  if os.listdir(file_dir):
    dir_id = get_parent_dir(service, file_path)

    copied_file = copy_file(file_dir)

    existing_files = get_drive_files(service, dir_id)
    print(existing_files)

    for f in os.listdir(file_dir):
      print(f)

      for f in range(0, len(existing_files)):
        fId = existing_files[f].get('name')
        print(fId)

      exit()

      mimetype = MimeTypes().guess_type(f)[0]
      

      file_metadata = {'name': f, 'parents': [dir_id]}
                      
      media = MediaFileUpload(os.path.join(file_dir, f), mimetype=mimetype)

      try:
        service.files().create(body=file_metadata,
                                      media_body=media,
                                      fields='id').execute()
      except Exception as ex:
        print("Exception %s " % ex)  

      f = None
  else:
    print("Directory %s is empty." % file_dir)


if __name__ == "__main__":
  main()