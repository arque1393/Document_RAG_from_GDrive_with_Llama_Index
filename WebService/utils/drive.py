# Basic Module 

import datetime 
import time 

# For OAuth and maintaining Drive Events 
from googleapiclient.errors import HttpError
from pathlib import Path
# for Retrieving data from Google Drive using Llama index 
from WebService.constants import ( GOOGLE_DRIVE_ACTIVITY_PAGE_SIZE,MS_CLIENT_ID,GRAPH_API_ENDPOINT,
                        ONE_DRIVE_ITEM_ENDPOINT,MONITORING_TIME_DELAY, TEMP_STORE_PATH, GDRIVE_ACCEPT_MIME_TYPES)
from typing import Any,Optional,Tuple,Iterable
import re
from WebService.db import models 

## OneDrive Utilities import 

import os
from threading import Thread
import requests
from llama_index.core import SimpleDirectoryReader

from WebService.utils.auth import MSAuth

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
        user_id : str
            The id of that specific user  
        callbacks (callable): the function that store the file content in Vector Database
    """
    user_disable = session.query(models.User).filter_by(user_id=user_id).first().disabled
    print("Background Thread is started  ")
    collection = session.query(models.Collection).filter_by(user_id=user_id).order_by(models.Collection.updated_at).first()
    while not user_disable:
        
            
        current_time = datetime.datetime.now()
        current_time_formate=current_time.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        previous_time_formate=collection.updated_at.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")+'+00:00'
        
        try:
            
            results = service.activity().query(body={
            "filter":f'time > "{previous_time_formate}" AND time < "{current_time_formate}"',
            # 'ancestorName':f"items/{collection.collection_id}",
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
        except Exception as e:
            # print(f"Error on fetching information of from folder {collection.collection_name} \n\n:", e)
            # print("Retrying.....")
            # time.sleep(5)
            # previous_time = current_time
            # exit()
            pass
        # Checking Condition
        time.sleep(MONITORING_TIME_DELAY)
        
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

def read_drive_folder(service,collection_name, callbacks):
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
    try:    
        results = service.files().list(
            pageSize=1000,  # Adjust as per your requirement
            fields="files(id, name, webViewLink, permissions)",
            q=f"'me' in owners and visibility='anyoneWithLink' and mimeType in {str(GDRIVE_ACCEPT_MIME_TYPES)[1:-1]} ",
            orderBy="modifiedTime desc"
        ).execute()
        files = results.get('files', [])        
        public_file_ids = [file['id'] for file in files]
        if not public_file_ids:
            return False 
    except Exception as e : 
        raise e
    try : 
        callbacks(public_file_ids,collection_name)
    except Exception as e :
        raise Exception (f'Callback running Error : {e}')
    return True
############################################################################################
################################ One Drive Access Utilities ################################
############################################################################################


class OneDriveReader():
    ''' Approximate Replicate of Llama Index's OneDriveLoader 
    '''
    def __init__(self,username:str, access_token:str) -> None:
        self.access_token = access_token
        self.temp_store_path = TEMP_STORE_PATH/username
        
    def _get_headers(self):
        access_token = self.access_token
        return {'Authorization': 'Bearer '+ access_token}
    def _extract_metadata(self, item):
        metadata = {}
        metadata['author'] = item['shared']['owner']['user']["displayName"]
        metadata['file_path'] = item.get('parentReference').get('path') + '/' + item.get('name')
        metadata['file name'] = item.get('name')
        metadata['created at'] = datetime.datetime.fromisoformat( item['createdDateTime'][:-1]).strftime("%Y-%m-%d %H:%M:%S")
        metadata['modified at'] = datetime.datetime.fromisoformat( item['lastModifiedDateTime'][:-1]).strftime("%Y-%m-%d %H:%M:%S")
        return metadata
    def _parse_folder_load_files(self,folder_id , recursive = True):
        response_file_info = requests.get(
                ONE_DRIVE_ITEM_ENDPOINT+rf'/{folder_id}/children',
                headers=self._get_headers()
            )
        file_dict = {}
        for item in response_file_info.json().get('value'): 
            if item.get('folder') and recursive :
                file_dict.update(self._parse_folder_load_files(item.get('id')))
            elif item.get('shared') and item.get('shared').get('scope') == 'users':
                metadata = self._extract_metadata(item)
                file_dict[item.get('id')] = metadata
                content = requests.get(
                    ONE_DRIVE_ITEM_ENDPOINT+rf'/{item.get("id")}/content',
                    headers=self._get_headers()).content
                file_extension = os.path.splitext(item.get("name"))[1]
                with open(self.temp_store_path / f'{item.get("id")}{file_extension}', 'wb')as f:
                    f.write(content)
        return file_dict
    def _remove_content(self,folder_path):
        folder = Path(folder_path)
        for item in folder.glob('*'):
            if item.is_file():
                item.unlink()  
            elif item.is_dir():
                self._remove_content(item)  
                item.rmdir() 
    def _load_files_from_file_ids(self,file_ids:str):
        file_dict={}
        for file_id in file_ids :
            response_file_info = requests.get(
                ONE_DRIVE_ITEM_ENDPOINT+rf'/{file_id}/',
                headers=self._get_headers())
            item = response_file_info.json()
            metadata = self._extract_metadata(item)
            file_dict[item.get('id')] = metadata
            content = requests.get(
                ONE_DRIVE_ITEM_ENDPOINT+rf'/{item.get("id")}/content',
                headers=self._get_headers()).content
            file_extension = os.path.splitext(item.get("name"))[1]
            if not self.temp_store_path.exists():
                self.temp_store_path.mkdir(parents=True)
            with open(self.temp_store_path / f'{item.get("id")}{file_extension}', 'wb')as f:
                f.write(content)
        
        return file_dict
            
    def load_data(self,folder_id:str|None =None, file_ids:Iterable[str]|None =None):
        if self.temp_store_path.exists():
            self._remove_content(self.temp_store_path)
        else : 
            self.temp_store_path.mkdir(parents=True)
        metadata={}
        
        if folder_id:
            metadata.update( self._parse_folder_load_files(folder_id))
        elif file_ids:
            metadata.update( self._load_files_from_file_ids(file_ids))
        else: raise Exception("folder_id and file_ids both can not be empty ")
        
        # print(metadata)
        documents = SimpleDirectoryReader(input_dir = self.temp_store_path.resolve().__str__(),
                            file_metadata = lambda file_name: metadata[os.path.splitext(os.path.basename(file_name))[0]]).load_data()
        self._remove_content(self.temp_store_path)
        return documents
    




### Define function to check Drive Updates
def watch_one_drive_load_data(session, user_name, user_id, callbacks : callable ):
    """Watch Drive check if any changes happens or not.
    This Works in a loop controlled by the db.models.User.disabled parameter. 
    If New File Uploaded or created or edited it extract the file ID and using callbacks store in to VectorStoreIndex

    Args:
        service : GoogleDriveService or Resource object  :
            Use to fetch Drive activity Information 
        session : FastAPI SessionLocal object : 
            Use to access specific users and collections. and also update the time. 
        user_id : str
            The id of that specific user  
        callbacks (callable): the function that store the file content in Vector Database
    """
    ms_auth = MSAuth(MS_CLIENT_ID)
    if ms_auth.get_token(user_name):
        user = session.query(models.User).filter_by(user_id=user_id).first()
        user.onedrive_disabled = True
        session.add(user)
        session.commit()
        session.refresh(user)
        raise Exception("Not Authenticated Error")
 
    activity_end_point = GRAPH_API_ENDPOINT+"/me/drive/recent"  
    headers={'Authorization': 'Bearer '+ ms_auth._access_token}
    user_disable = session.query(models.User).filter_by(user_id=user_id).first().one_drive_disabled
    print("OneDrive Background Thread is started  ")
    collection = session.query(models.Collection).filter_by(user_id=user_id).order_by(models.Collection.one_drive_updated_at).first()
    while not user_disable:
        # print('running One drive')
        current_time = datetime.datetime.now()
        current_time_formate=current_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        previous_time_formate=collection.one_drive_updated_at.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'        
        try:            
            filter_query = f"lastModifiedDateTime lt {current_time_formate} and lastModifiedDateTime gt {previous_time_formate} "
            # Parameters for the request
            params = {'$filter': filter_query}
            response  = requests.get(activity_end_point,params=params, headers=headers).json()
            try:
                file_ids =[activity.get("id")for activity in response['value'] ]
            except:
                raise Exception(str(response))
            file_list=list(set(file_ids))
            # print(file_list)
            if file_list:
                print('reading new files : ',file_list)
                try:
                    callbacks(user_name, ms_auth._access_token, file_list)
                    print('Reading Successful.')
                except Exception as e:
                    print("Error Occurs while Reading")
                    print(e)
                finally:
                    print("Server is waiting for next update in google drive ")
            collection.one_drive_updated_at = current_time
            session.commit()
            session.refresh(collection)

        except Exception as e:
            pass
        user_disable = session.query(models.User).filter_by(user_id=user_id).first().one_drive_disabled
        
