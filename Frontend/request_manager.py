
from cryptography.fernet import Fernet
import requests
key = b'XCZhJ6fcinvUorn-xrnW6uPYcMbm59cbksIpxQB-ADo=' # For local Encryption



class NotAuthenticatedException(Exception):    
    def __init__(self, message="You are Not Authenticated", **kwargs):
        self.message = message
    def __str__(self):
        return self.message
    


def get_token ():
    with open('token.b','rb')as f:
        encrypted_token = f.read()
    cipher_suite = Fernet(key)
    decrypted_token = cipher_suite.decrypt(encrypted_token).decode()
    return decrypted_token
        
def save_token(token):    
    cipher_suite = Fernet(key)
    encrypted_token = cipher_suite.encrypt(token.encode())
    with open('token.b','wb')as f:
        f.write(encrypted_token)
        
def send_query(question,collection_name):
    try : 
        access_token = get_token()
    except: 
        raise NotAuthenticatedException()
    
    
    url = 'http://127.0.0.1:8000/user/query'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "collection_name": str(collection_name),
        "question":str(question)
    }
    response = requests.post(url, headers=headers, json=data)
    return  response.json()
    
def login_req(username,password):
    url = 'http://127.0.0.1:8000/token'
    headers = {'accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded'}
    login_data = {"username": username, "password": password}
    
    response = requests.post(url, headers=headers, data=login_data)
    try:
        access_token =  response.json()['access_token']
        save_token(access_token)
        return ('success',"None")
    except Exception as e:
        detail = response.json()['detail']
        return ('failed',f"Login Error:{detail}")
        
    # print("Login Done")
def signup_req(username,email,password):

    url = 'http://127.0.0.1:8000/user'
    headers = {'accept': 'application/json','Content-Type': 'application/json'}
    data = {"username": username,"email": email,"password": password}
    response = requests.post(url, headers=headers, json=data)
    try:
        access_token =  response.json()['access_token']
        save_token(access_token)
        return ('success',"None")
    except Exception as e:
        detail = response.json()['detail']
        return ('failed',f"Signup Error:{detail}")
def get_collections():
    url = 'http://127.0.0.1:8000/user/collections'
    try:
        access_token = get_token()
    except:
        raise NotAuthenticatedException()
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    try: 
        collection_list = [collection['collection_name']for collection in response.json()]
        return collection_list
    except:
        return response.json()['detail']
    

def create_collection(folder_link):
    url = 'http://127.0.0.1:8000/user/collections'
    try : 
        access_token = get_token()    
    except: 
        raise NotAuthenticatedException()
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {"folder_link": folder_link}
    response = requests.post(url, headers=headers, json=data)
    return response.json()