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

from pathlib import Path
# for Retrieving data from Google Drive using Llama index 
from constants import ( GOOGLE_DRIVE_ACTIVITY_PAGE_SIZE,MONITORING_TIME_DELAY)
from typing import Any,Optional,Tuple
import re

from db import models 

# Helper Function to extract file IDs 
def extract_file_ids(target_list:list[Any]):
    return [target['driveItem']['name'][6:] for target in target_list 
            if target['driveItem']['mimeType'] != 'application/vnd.google-apps.folder']

reader_activity_list:list[str] = ['create','edit','rename']
remove_activity:str = 'delete'



### Define function to check Drive Updates
def watch_drive_load_data(service, session, user_id, callbacks : callable ):
    """Watch Drive check if any changes happens or not.
    If New File Uploaded or created or edited it extract the file ID and using callbacks store in to VectorStoreIndex

    Args:
        folder_id (str): The id of that specific folder of google drive Where to search changes 
        callbacks (callable): the function that store the file content in Vector Database
    """
    user_disable = session.query(models.User).filter_by(user_id=user_id).first().disabled
    print("Background Thread is started  ")
    while not user_disable:
        collections = session.query(models.Collection).filter_by(user_id=user_id).order_by(models.Collection.updated_at).all()
        for collection in collections : 
            
            current_time = datetime.datetime.now()
            current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
            previous_time_formate=collection.updated_at.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
            
            try:
                results = service.activity().query(body={
                "filter":f'time > "{previous_time_formate}" AND time < "{current_time_formate}"',
                'ancestorName':f"items/{collection.collection_id}",
                "pageSize": GOOGLE_DRIVE_ACTIVITY_PAGE_SIZE}).execute()
                
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
                        callbacks(file_list,collection.collection_id)
                        print('Reading Successful.')
                    except Exception as e:
                        print("Error Occurs while Reading")
                        print(e)
                    finally:
                        print("Server is waiting for next update in google drive ")
                collection.updated_at = current_time
                session.commit()
                session.refresh(collection)
            # time.sleep(MONITORING_TIME_DELAY)
            except Exception as e:
                print(f"Error on fetching information of from folder {collection.collection_name} :", e)
                print("Retrying.....")
                # time.sleep(5)
                # previous_time = current_time
                # exit()
            
        # Checking Condition
        user_disable = session.query(models.User).filter_by(user_id=user_id).first().disabled
        


def drive_link_to_folder_name_and_id ( service, folder_link:str)-> Tuple[str,str]:
    pattern = r'/folders/([\w-]+)'
    match = re.search(pattern, folder_link)
    
    if match:   
        folder_id = match.group(1)
    else : 
        raise Exception("Regular Expression not match ")
    folder_info = service.files().get(fileId=folder_id, fields="name").execute()
    return (str(folder_info['name']),folder_id)
    # return folder_link

def read_drive_folder(service,folder_id,folder_name, callbacks, update_time:Optional[Any]=None):
    if not update_time:
        update_time = datetime.datetime.now() - datetime.timedelta(days=365)
    while True:
        current_time = datetime.datetime.now()
        current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        update_time_formate=update_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        
        try:
            results = service.activity().query(body={
            "filter":f'time > "{update_time_formate}" AND time < "{current_time_formate}"',
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
        print("documents lodes : ", file_list)
        if file_list:
            print('reading new files : ',file_list)
            try:
                callbacks(file_list,folder_name)
                print('Reading Successful.')
            except Exception as e:
                print("Error Occurs while Reading")
                print(e)
            finally:
                print("Server is waiting for next update in google drive ")
        time.sleep(MONITORING_TIME_DELAY) 
        break 