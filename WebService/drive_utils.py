# Basic Module 

import datetime 
import time 

# For OAuth and maintaining Drive Events 
from googleapiclient.errors import HttpError
from pathlib import Path
# for Retrieving data from Google Drive using Llama index 
from constants import ( GOOGLE_DRIVE_ACTIVITY_PAGE_SIZE,
                       ONE_DRIVE_ITEM_ENDPOINT,MONITORING_TIME_DELAY, TEMP_STORE_PATH)
from typing import Any,Optional,Tuple
import re
from db import models 

## OneDrive Utilities import 
import webbrowser
from datetime import datetime
import json
import os
import msal
from threading import Thread
import requests
from llama_index.core import SimpleDirectoryReader



class DriveFolderDoesNotExist(Exception):
    def __init__(self, message = "Unable to find the folder ID in your Google Drive Account.\n Do not enter shared folder's link.") -> None:
        super().__init__()
        self.message = message
    def __raper__(self):
        return self.message
    def __self__(self):
        return self.message
# Helper Function to extract file IDs 
def extract_file_ids(target_list:list[Any]):
    return [target['driveItem']['name'][6:] for target in target_list 
            if target['driveItem']['mimeType'] != 'application/vnd.google-apps.folder']

reader_activity_list:list[str] = ['create','edit','rename']
remove_activity:str = 'delete'

def check_folder_permission(service, folder_id):
    try:
        permissions = service.permissions().list(fileId=folder_id, fields="permissions(type)").execute()
        return (iter(permissions['permissions']).__next__()['type'])
    except HttpError  as e:
        if e.status_code == 500:
            raise DriveFolderDoesNotExist()
        elif e.status_code ==403:
            raise Exception(message = "This Folder belongs to another Google Account")            
        else :
            raise Exception(f"{e}")

### Define function to check Drive Updates
def watch_drive_load_data(service, session, user_id, callbacks : callable ):
    """Watch Drive check if any changes happens or not.
    This Works in a loop controlled by the db.models.User.disabled parameter. 
    If New File Uploaded or created or edited it extract the file ID and using callbacks store in to VectorStoreIndex

    Args:
        service : GoogleDriveService or Resource object  :
            Use to fetch Drive activity Information 
        session : FastAPI SessionLocal object : 
            Use to access specific users and collections. and also update the time. 
        user_if : str
            The id of that specific user  
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
                        callbacks(file_list,collection.collection_name)
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
                # print(f"Error on fetching information of from folder {collection.collection_name} \n\n:", e)
                # print("Retrying.....")
                # time.sleep(5)
                # previous_time = current_time
                # exit()
                pass
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
    """Watch Drive check if any changes happens or not.
    This Works only once If New File Uploaded or created or edited it extract the file ID and using callbacks store in to VectorStoreIndex

    Args:
        service : GoogleDriveService or Resource object  :
            Use to fetch Drive activity Information 
        folder_id: str 
            Use to fetch data from google 
        folder_name : str
            Use to pass callback as collection name   
        callbacks (callable): the function that store the file content in Vector Database
        
        update_time:str 
            If available then search activities after updated time 
    """
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
        except HttpError as e:
            if e.status_code == 500:
                raise DriveFolderDoesNotExist()
            else : 
                raise Exception(f'{e}')
        except Exception as e : 
            raise  e
        time.sleep(MONITORING_TIME_DELAY) 
        break 
    
    
    
############################################################################################
################################ One Drive Access Utilities ################################
############################################################################################

class OneDriveReader():
    def __init__(self, access_token) -> None:
        self.access_token = access_token
        
    def _get_headers(self):
        access_token = self.access_token()
        return {'Authorization': 'Bearer '+ access_token['access_token']}
    
    def _parse_folder_load_files(self,folder_id , recursive = True):
        response_file_info = requests.get(
                ONE_DRIVE_ITEM_ENDPOINT+rf'/{folder_id}/children',
                headers=self._get_headers()
            )
        file_dict = {}
        # print(response_file_info.json())
        # display(response_file_info.json())
        for item in response_file_info.json().get('value'): 
            if item.get('folder') and recursive :
                file_dict.update(self._parse_folder_load_files(item.get('id')))
            elif item.get('shared') and item.get('shared').get('scope') == 'users':

                metadata = {}
                metadata['author'] = item['shared']['owner']['user']["displayName"]
                metadata['onedrive_path'] = item.get('parentReference').get('path') + '/' + item.get('name')
                metadata['created_at'] = datetime.fromisoformat( item['createdDateTime'][:-1])
                metadata['updated_at'] = datetime.fromisoformat( item['lastModifiedDateTime'][:-1])
                file_dict[item.get('id')] = metadata
                content = requests.get(
                    ONE_DRIVE_ITEM_ENDPOINT+rf'/{item.get("id")}/content',
                    headers=self._get_headers()).content
                file_extension = os.path.splitext(item.get("name"))[1]
                with open(TEMP_STORE_PATH / f'{item.get("id")}{file_extension}', 'wb')as f:
                    f.write(content)
        return file_dict
    def _remove_content(self,folder_path):
        folder = Path(folder_path)
        for item in folder.glob('*'):
            if item.is_file():
                item.unlink()  
            elif item.is_dir():
                self.remove_content(item)  
                item.rmdir() 

    def load_data(self, folder_id:str):
        if TEMP_STORE_PATH.exists():
            self._remove_content(TEMP_STORE_PATH)
        else : 
            TEMP_STORE_PATH.mkdir(parents=True)
        metadata  = self._parse_folder_load_files(folder_id)
        
        documents = SimpleDirectoryReader(input_dir = TEMP_STORE_PATH.resolve().__str__()
                            file_metadata = lambda file_name:metadata[file_name.split('.')[0]]
                                    ).load_data()
        self._remove_content(TEMP_STORE_PATH)
        return documents
    