import webbrowser
from datetime import datetime
import json
import os
import time
import msal
from threading import Thread
import requests
from pathlib import Path 
import re 
from llama_index.core import SimpleDirectoryReader
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
ONE_DRIVE_ITEM_ENDPOINT = GRAPH_API_ENDPOINT + r'/me/drive/items'
SCOPES = ['Files.Read']
LOGIN_EXPIRE_DURATION = 300
TEMP_STORE_PATH = Path('./tmp_au4os42asx4fgj45mz9db4zj5r3xd7ghm/')

class OneDriveReader(object):
    def __init__(self, client_id) -> None:
        self.client_id = client_id
        self.user_token = None
        self.__access_token = None
    def _get_access_token(self):
        start_time = time.time()
        while True : 
            if time.time() - start_time > LOGIN_EXPIRE_DURATION  : 
                raise Exception("Access Token is not fount")
            if not self.__access_token :
                continue 
            break
        return self.__access_token
    def _get_headers(self):
        access_token = self._get_access_token()
        return {'Authorization': 'Bearer '+ access_token['access_token']}
    def _save_access_token(self,client,flow,access_token_cache):        
        webbrowser.open('https://microsoft.com/devicelogin')
        token_response = client.acquire_token_by_device_flow(flow)
        self.__access_token =  token_response
        with open('ms_graph_api_token.json', 'w') as _f:
            _f.write(access_token_cache.serialize())
            
    def get_access_token(self):
        access_token_cache = msal.SerializableTokenCache()
        flow = None
        if os.path.exists('ms_graph_api_token.json'):
            with open("ms_graph_api_token.json", "r") as token_file : 
                token_str = token_file.read()
            access_token_cache.deserialize(token_str)
            access_token = json.loads(token_str)['AccessToken']
            token_expiration = datetime.fromtimestamp(
                int(access_token[iter(access_token).__next__()]['expires_on']))
            if datetime.now() > token_expiration:
                os.remove('ms_graph_api_token.json')
                access_token_cache = msal.SerializableTokenCache()
        # assign a SerializableTokenCache object to the client instance
        client = msal.PublicClientApplication(client_id=self.client_id, token_cache=access_token_cache)

        if accounts:= client.get_accounts():
            token_response = client.acquire_token_silent(SCOPES, accounts[0])
            self.__access_token = token_response
        else:
            flow = client.initiate_device_flow(scopes=SCOPES)
            # webbrowser.open('https://microsoft.com/devicelogin')
            # token_response = client.acquire_token_by_device_flow(flow)
            Thread(target=lambda:self._save_access_token(client,flow,access_token_cache)).start()
            time.sleep(0.1)
        if flow : 
            return flow.get('user_code')
        
    def _parse_folder_load_files(self, folder_id , recursive = True):
        response_file_info = requests.get(
                ONE_DRIVE_ITEM_ENDPOINT+rf'/{folder_id}/children',
                headers=self._get_headers()
            )
        file_dict = {}
        # display(response_file_info.json())
        for item in response_file_info.json().get('value'): 
            if item.get('folder') and recursive :
                file_dict.update(self._parse_folder_load_files(item.get('id')))
            else :
                
                file_dict[item.get('id')] = item.get('name')
                content = requests.get(
                    ONE_DRIVE_ITEM_ENDPOINT+rf'/{item.get("id")}/content',
                    headers=self._get_headers()).content
                with open(TEMP_STORE_PATH / f'{item.get("name")}', 'wb')as f:
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
        self._parse_folder_load_files(folder_id)
        documents = SimpleDirectoryReader(input_dir = TEMP_STORE_PATH.resolve().__str__()).load_data()
        self._remove_content(TEMP_STORE_PATH)
        return documents
    
    
    
def extract_id_from_one_drive_link(shortened_url):
    try:
        response = requests.get(shortened_url, allow_redirects=True)
        if response.status_code == 200:
            pattern = r"id=([a-zA-Z0-9!]+)&" 
            if match:= re.search(pattern, response.url):            
                return match.group(1)           
        else:
            print("Failed to expand the OneDrive URL.")
            return None
    except requests.exceptions.RequestException as e:
        print("Error:", e)
        return None


    
    
if __name__=='__main__':
    client_id  =  '8c849b5d-cd74-4e8f-adc9-d7534074b99b'
    share_link = 'https://1drv.ms/f/s!Aj2Nbw_0FL8HjagQQk9_gLSe6ZI9Cg?e=PRPUjd'
    folder_id = extract_id_from_one_drive_link(share_link)
    od_reader = OneDriveReader(client_id)
    user_code = od_reader.get_access_token()
    print(user_code)
    print(od_reader._get_access_token())
    
    # docs = od_reader.load_data(folder_id)
    # print (docs)