# Basic Module 
import os.path
import datetime 
import time 

# For OAuth and maintaining Drive Events 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# for Retrieving data from Google Drive using Llama index 
from constants import ( DRIVE_API_SCOPES,
        MONITORING_TIME_DELAY, GOOGLE_CLIENT_SECRET)
from typing import Any

## Define Credential to Google Drive 
credentials:Any = None
if os.path.exists("../Google_Credentials/token.json"):
    credentials = Credentials.from_authorized_user_file("../Google_Credentials/token.json", DRIVE_API_SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not credentials or not credentials.valid:
    # if credentials and credentials.expired and credentials.refresh_token:
    #     credentials.refresh(Request())
    # else:
    flow = InstalledAppFlow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRET,
        DRIVE_API_SCOPES
    )
    credentials = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("../Google_Credentials/token.json", "w") as token:
        token.write(credentials.to_json())
service = build("driveactivity", "v2", credentials=credentials)

print("Service is made ")
from constants import DRIVE_FOLDER_ID


# Helper Function to extract file IDs 
def extract_file_ids(target_list:list[Any]):
    return [target['driveItem']['name'][6:] for target in target_list 
            if target['driveItem']['mimeType'] != 'application/vnd.google-apps.folder']


reader_activity_list:list[str] = ['create','edit','rename']
remove_activity:str = 'delete'



### Define function to check Drive Updates
def watch_drive_load_data(folder_id : str, callbacks : callable ):
    """Watch Drive check if any changes happens or not.
    If New File Uploaded or created or edited it extract the file ID and using callbacks store in to VectorStoreIndex

    Args:
        folder_id (str): The id of that specific folder of google drive Where to search changes 
        callbacks (callable): the function that store the file content in Vector Database
    """
    previous_time = datetime.datetime.now() - datetime.timedelta(days=365)    
    while True:
        current_time = datetime.datetime.now()
        current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        previous_time_formate=previous_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        
        try:
            results = service.activity().query(body={
            "filter":f'time > "{previous_time_formate}" AND time < "{current_time_formate}"',
            'ancestorName':f"items/{folder_id}",
            "pageSize": 2}).execute()
        except Exception as e:
            print("Error on fetching information of drive :", e)
            print("Retrying.....")
            time.sleep(5)
            # previous_time = current_time
            # exit()
            continue 
            
        activities = results.get('activities', [])
        deleted_file_list=[]
        file_list:list[str] = []
        for activity in activities:
            if iter(activity['primaryActionDetail']).__next__() in reader_activity_list :
                file_list+=extract_file_ids(activity['targets'])
            if iter(activity['primaryActionDetail']).__next__() == remove_activity :
                deleted_file_list+=extract_file_ids(activity['targets'])
        for item in file_list :
            if item in deleted_file_list:
                file_list.remove(item)
        
        file_list=list(set(file_list))
        # print("documents lodes : ", callbacks(file_list))
        if file_list:
            print('reading new files : ',file_list)
            try:
                callbacks(file_list,folder_id)
                print('Reading Successful.')
            except Exception as e:
                print("Error Occurs while Reading")
                print(e)
            finally:
                print("Server is waiting for next update in google drive ")
        previous_time = current_time
        time.sleep(MONITORING_TIME_DELAY)
        


def drive_link_to_id (folder_link:str)->str:
    
    front = 'https://drive.google.com/drive/folders/'
    end = '?usp=sharing'
    return folder_link.strip(end).strip(front)

def folder_id_to_name(folder_id):
    pass 
def read_drive_folder(folder_id):
    while True:
        current_time = datetime.datetime.now()
        current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        previous_time_formate=previous_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        
        try:
            results = service.activity().query(body={
            "filter":f'time > "{previous_time_formate}" AND time < "{current_time_formate}"',
            'ancestorName':f"items/{folder_id}",
            "pageSize": 2}).execute()
        except Exception as e:
            print("Error on fetching information of drive :", e)
            print("Retrying.....")
            time.sleep(5)
            # previous_time = current_time
            # exit()
            continue 
            
        activities = results.get('activities', [])
        deleted_file_list=[]
        file_list:list[str] = []
        for activity in activities:
            if iter(activity['primaryActionDetail']).__next__() in reader_activity_list :
                file_list+=extract_file_ids(activity['targets'])
            if iter(activity['primaryActionDetail']).__next__() == remove_activity :
                deleted_file_list+=extract_file_ids(activity['targets'])
        for item in file_list :
            if item in deleted_file_list:
                file_list.remove(item)
        
        file_list=list(set(file_list))
        # print("documents lodes : ", callbacks(file_list))
        if file_list:
            print('reading new files : ',file_list)
            try:
                callbacks(file_list,folder_id)
                print('Reading Successful.')
            except Exception as e:
                print("Error Occurs while Reading")
                print(e)
            finally:
                print("Server is waiting for next update in google drive ")
        previous_time = current_time
        time.sleep(MONITORING_TIME_DELAY) 
        break 