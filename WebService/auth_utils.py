from models import TokenData,User
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from pydantic import EmailStr
from jose import JWTError, jwt
from cryptography.fernet import Fernet
from pathlib import Path 
import json
from typing import Annotated,Any
from db.setup import get_session, Base
from db import models 
from sqlalchemy.orm import Session
import webbrowser
import msal

import time 
from threading import Thread
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
SCOPES = ['Files.Read']
CLIENT_ID = '8c849b5d-cd74-4e8f-adc9-d7534074b99b'


# Google Authentication Service 
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from constants import  (JWT_AUTH_SECRET_KEY , ALGORITHM, ONEDRIVE_LOGIN_EXPIRE_DURATION,
    GOOGLE_CLIENT_SECRET, DRIVE_API_SCOPES, ONEDRIVE_SCOPE,FERNET_KEY,ONEDRIVE_CREDENTIAL_DIR)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
cipher_suite = Fernet(FERNET_KEY)

def is_email_or_username_taken(email: EmailStr,username:str, model:Base , session:Session ) -> bool | str:
    '''check in database the given email is already exist or not
input:
    email : Email String
    model : model or table where to check
    session : SQLAlchemy Database Session Utility 
return str: 
    return 'email' if email exist 
    return 'username' if username exist 
    return None for new user 
'''
    existing_object = session.query(model).filter_by(email=email).first()
    if existing_object  : 
        return 'email' 
    existing_object = session.query(model).filter_by(username=username).first()
    if existing_object:
        return 'username'
    return False
    
## Helper Functions 
def verify_password(plain_password, hashed_password):
    """Password Verification by converting Hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Return Hash of any string """
    return pwd_context.hash(password)



    

def authenticate_user(username: str, password: str, session:Session):
    """Authenticated an user"""
    if user := session.query(models.User).filter_by(username=username).first():
        return user if verify_password(password, user._password_hash) else False
    else: return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Create Access Token usning Openssl Secret key """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode["exp"] = expire
    return  jwt.encode(to_encode, JWT_AUTH_SECRET_KEY, algorithm=ALGORITHM)



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],session:Session=Depends(get_session)):
    """Authenticate user and return current user if authentication success"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if user := session.query(models.User).filter_by(username=username).first():
        return user
    raise credentials_exception
    


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    # """Return Users if only user is active"""
    # if current_user.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




def google_auth(username):
    """Create authentication token by Google for connecting drive and access Drive files and Drive Activity. Store the Google Token in side server file store and using this credential token build two services 
        1. Google Drive Service (V3)
        2. Google Drive Activity Service (V2)
    Args:
        username (): Identify the the token using username 
    Returns:
        Tuple of Two Service of Google Drive 
    """

    credentials:Any = None
    token_path = Path(fr"./CredentialHub/{username}").resolve()
    if not token_path.exists():
        token_path.mkdir(parents=True)
        
    def create_token():
        """Create Google Drive Access Token and Refresh token using OAuth2 Client Secret 
        Returns:
            dict: Json stile dict containing Access token and Refresh token  
        """
        flow = InstalledAppFlow.from_client_secrets_file(
            GOOGLE_CLIENT_SECRET,
            DRIVE_API_SCOPES
        )
        credentials = flow.run_local_server(port=0)
        with open(token_path/'token.b', "wb") as token:
            encrypted_token = cipher_suite.encrypt(credentials.to_json().encode())
            token.write(encrypted_token)            
        return credentials
    
    if (token_path/'token.b').exists():
        with open(token_path/'token.b','rb') as f:
            decrypted_token = cipher_suite.decrypt(f.read()).decode()
            token_dict = json.loads(decrypted_token)
        credentials = Credentials.from_authorized_user_info(token_dict, DRIVE_API_SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            try:
                credentials.refresh(Request())
            except : 
                credentials = create_token()
        else:
            credentials = create_token()
    drive_service = build("drive", "v3", credentials=credentials)
    drive_activity_service = build("driveactivity", "v2", credentials=credentials)
    
    return (drive_service,drive_activity_service)







class MSAuth():
    def __init__(self, client_id) -> None:
        self.client_id = client_id
        self.user_token = None
        self.__token_response = None
        self.__access_token = None
        self.__refresh_token = None 
    @property
    def _token_response(self):
        start_time = time.time()
        while True : 
            if time.time() - start_time > ONEDRIVE_LOGIN_EXPIRE_DURATION  : 
                raise Exception("Access Token is not fount")
            if not self.__token_response :
                continue 
            break
        return self.__token_response
    @property
    def _access_token(self):
        start_time = time.time()
        while True : 
            if time.time() - start_time > ONEDRIVE_LOGIN_EXPIRE_DURATION  : 
                raise Exception("Access Token is not fount")
            if not self.__access_token :
                continue 
            break
        return self.__access_token
    @property
    def _refresh_tokene(self):
        start_time = time.time()
        while True : 
            if time.time() - start_time > ONEDRIVE_LOGIN_EXPIRE_DURATION  : 
                raise Exception("Access Token is not fount")
            if not self.__refresh_token :
                continue 
            break
        return self.__refresh_token
    # Done 
    def _write_token(self, token_path:Path, serialized_token_cache:str):
        
        cipher_suite = Fernet(FERNET_KEY)
        with open(token_path, "wb") as token:
            encrypted_token = cipher_suite.encrypt(serialized_token_cache.encode())
            token.write(encrypted_token)  
    def _read_token(self,token_path):
        cipher_suite = Fernet(FERNET_KEY) 
        if not (token_path).exists():
            raise Exception("Token File is not found")
        with open(token_path, "rb") as token:
            encrypted_token = token.read()
            serialized_token_cache = cipher_suite.decrypt(encrypted_token).decode()
        return serialized_token_cache
        
    def _save_token(self,client,flow,token_cache, token_path):        
        webbrowser.open('https://microsoft.com/devicelogin')
        token_response = client.acquire_token_by_device_flow(flow)
        self.__token_response =  token_response
        self.__access_token = token_response['access_token']
        self.__refresh_token = token_response['refresh_token']
        self._write_token(token_path,token_cache.serialize() )

    def get_token(self,username:str):
        token_dir =  ONEDRIVE_CREDENTIAL_DIR/username
        if not token_dir.exists():
            token_dir.mkdir(parents=True)
        access_token_path = ONEDRIVE_CREDENTIAL_DIR/username/'token.b'
        token_cache = msal.SerializableTokenCache()
        if access_token_path.exists():
            token_str = self._read_token(access_token_path)
            token_cache.deserialize(token_str)
            token_dict = json.loads(token_str)
            access_token = token_dict['AccessToken']
            token_expiration = datetime.fromtimestamp(
                int(access_token[iter(access_token).__next__()]['expires_on']))
            if datetime.now() > token_expiration:
                try : 
                    client = msal.PublicClientApplication(client_id=CLIENT_ID,token_cache=token_cache)
                    refresh_token =  token_dict['RefreshToken']
                    refresh_token_secret = refresh_token[iter(refresh_token).__next__()]['secret']
                    token_response = client.acquire_token_by_refresh_token(refresh_token_secret, SCOPES)
                    self._write_token(token_cache.serialize())                    
                    self.__access_token = token_response['access_token']   
                    self.__access_token = token_response['refresh_token']
                    return None 
                except:
                    pass
            else : 
                self.__access_token = access_token[iter(access_token).__next__()]['secret']
                refresh_token = token_dict['RefreshToken']
                self.__refresh_token = refresh_token[iter(refresh_token).__next__()]['secret']
                return None
            
    
        # token_cache = msal.SerializableTokenCache()
        client = msal.PublicClientApplication(client_id=self.client_id, token_cache=token_cache)

        if accounts:= client.get_accounts():
            token_response = client.acquire_token_silent(ONEDRIVE_SCOPE, accounts[0])
            self.__token_response = token_response
            self.__access_token = token_response['access_token']   
            # self.__access_token = token_response['refresh_token']
            return None
        else:
            flow = client.initiate_device_flow(scopes=ONEDRIVE_SCOPE)
            thread = Thread(target=(lambda:self._save_token(client,flow,token_cache,access_token_path)))
            thread.start()
            time.sleep(0.1)        
            return flow.get('user_code')
        
    






    
        
    
# if __name__=='__main__':
#     client_id  =  '8c849b5d-cd74-4e8f-adc9-d7534074b99b'
#     # share_link = 'https://1drv.ms/f/s!Aj2Nbw_0FL8HjagQQk9_gLSe6ZI9Cg?e=PRPUjd'
#     # folder_id = extract_id_from_one_drive_link(share_link)
#     ms_auth = MSAuth(client_id)
#     user_code = ms_auth.get_token()
#     print(user_code)
#     access_token = ms_auth._access_token
#     print(access_token)
#     # docs = ms_auth.load_data(folder_id)
#     # print (docs)