import os.path
import datetime 
import time 

# For maintaining Drive Events 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# for Retrieving data from Google Drive using Llamaindex 
from llama_index.readers.google import GoogleDriveReader
from constants import GOOGLE_CREDENTIALS_PATH, DRIVE_API_SCOPES, GOOGLE_CLIENT_SECRET
from typing import Any

loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH)

def load_data_from_drive_folder(folder_id: str):
    docs = loader.load_data(folder_id=folder_id)
    if not docs :
        raise Exception("Content Load Error","No content is loaded")
        
    return docs



### Define function to check Drive Updates 

## Define Credential to Google Drive 
credentials:Any = None
if os.path.exists("token.json"):
    credentials = Credentials.from_authorized_user_file("token.json", DRIVE_API_SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not credentials or not credentials.valid:
    if credentials and credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRET,
            DRIVE_API_SCOPES
        )
    credentials = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(credentials.to_json())
service = build("driveactivity", "v2", credentials=credentials)

print("Service is made ")
from constants import DRIVE_FOLDER_ID

obj = None
def callbacks(obj:dict,container:object):
        container = obj
def watch_drive(folder_id : str, callbacks : callable):
    previous_time = datetime.datetime.now() - datetime.timedelta(seconds=10)    
    while True:
        current_time = datetime.datetime.now()
        current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        previous_time_formate=previous_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'

        results = service.activity().query(body={
                "filter":f'time > "{previous_time_formate}" AND time < "{current_time_formate}"',
                ## `time >= "2016-01-10T01:02:03-05:00"`
                'ancestorName':f"items/{folder_id}",
                "pageSize": 2}).execute()
        
        activities = results.get('activities', [])
        previous_time = current_time
        time.sleep(10)
        # print(load_data_from_drive_folder(DRIVE_FOLDER_ID))
        print(activities)
        
watch_drive(DRIVE_FOLDER_ID,callbacks)


