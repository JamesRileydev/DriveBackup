from __future__ import print_function
import os
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaFileUpload
from mimetypes import MimeTypes
from configparser import ConfigParser
import manage


SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE = ''


def create_drive_dir(drive_dir):
    file_metadata = {
        'name': drive_dir,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    folder = SERVICE.files().create(body=file_metadata,
                                    fields='id').execute()
    return folder.get('id')


def create_service(file_path):
    global SERVICE
    token_path = os.path.abspath(os.path.join(
        file_path, 'files\\', 'token.json'))

    creds = None

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as ex:
                print("Token has expired: \n%s" % ex)
                exit(1)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

    with open(token_path, 'w') as token:
        token.write(creds.to_json())

    SERVICE = build('drive', 'v3', credentials=creds)


def get_drive_file_ids(drive_dir_id):
    q = "'%s' in parents" % drive_dir_id
    print(q)

    results = SERVICE.files().list(q=q,
                                   pageSize=10,
                                   fields="nextPageToken, files(id)").execute()
    items = results.get('files')

    files_list = []
    for i in items:
        id = i.get('id')
        files_list.append(id)

    return(files_list)


def get_drive_id(dir_name):
        page_token = None
        name = "name='%s'" % dir_name
        try:
            response = SERVICE.files().list(q=name,
                                            spaces='drive',
                                            fields='nextPageToken, files(id, name)',
                                            pageToken=page_token).execute()
        except Exception as ex:
            print("Exception %s " % ex)

        if not response.get('files', []):
            print("No id found for file, creating directory in Google Drive")

            return create_drive_dir(name)

        else:
            for file in response.get('files', []):
                dir_id = file.get('id')

            return dir_id


def move_drive_files(files_in_drive, drive_copy_id):
    for f in files_in_drive:
        if f != drive_copy_id:
            print(f)
            file = SERVICE.files().get(fileId=f,
                                       fields='parents').execute()
            previous_parents = ",".join(file.get('parents'))
            # Move the file to the new folder
            file = SERVICE.files().update(fileId=f,
                                          addParents=drive_copy_id,
                                          removeParents=previous_parents,
                                          fields='id, parents').execute()


def upload_files(copied_files_dir, drive_id):
    if os.listdir(copied_files_dir):
        for f in os.listdir(copied_files_dir):
            mimetype = MimeTypes().guess_type(f)[0]
            file_metadata = {'name': f, 'parents': [drive_id]}
            media = MediaFileUpload(os.path.join(
                copied_files_dir, f), mimetype=mimetype)

            try:
                SERVICE.files().create(body=file_metadata,
                                       media_body=media,
                                       fields='id').execute()
            except Exception as ex:
                print("Exception %s " % ex)

            print(f)
            f = None

    else:
        print("Directory %s is empty." % copied_files_dir)
