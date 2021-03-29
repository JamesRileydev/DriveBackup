from __future__ import print_function
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from mimetypes import MimeTypes

SCOPES = ['https://www.googleapis.com/auth/drive']

def main():
  filepath = os.path.dirname(os.path.realpath(__file__))
  print(filepath)
  token_path = os.path.abspath(os.path.join(filepath, 'files\\', 'token.json'))
  print(token_path)
  # sys.exit()

  user = os.getlogin()
  print(user)

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

  # results = service.files().list(
  #   pageSize=10, fields="nextPageToken, files(id, name)").execute()
  # items = results.get('files', [])

  file_dir  = os.path.dirname(r'C:\Users\%s\DriveBackup\\' % user)
  print(file_dir)

  # for file in file_dir:
  mimetype = MimeTypes().guess_type('files/drive_test.txt')[0]

  file_metadata = {'name': 'drive_test.txt'}
  media = MediaFileUpload('files/drive_test.txt', mimetype=mimetype)

  try:
    file = service.files().create(body=file_metadata,
                                        media_body=media,
                                        fields='id').execute()
  except Exception as ex:
    print("Exception %s " % ex)  

  print('File ID: %s' % file.get('id'))

  print("Completed")
  # if not items:
  #   print('No files found.')
  # else:
  #   print('Files:')
  #   for item in items:
  #     print(u'{0} ({1})'.format(item['name'], item['id']))

if __name__ == "__main__":
  main()