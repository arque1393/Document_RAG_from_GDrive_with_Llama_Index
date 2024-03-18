# Here are some Global Constants variables 
from pathlib import Path 
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
from dotenv import load_dotenv
BASE_DIR = Path(__file__).resolve().parent

load_dotenv()
## Please Change the Path according to your Google Credential Json
GOOGLE_CREDENTIALS_PATH = BASE_DIR.parent/'Google_Credentials'/'PROJECT_ID.json'
GOOGLE_CLIENT_SECRET = BASE_DIR.parent/'Google_Credentials'/'CLIENT_SECRET.json'
VECTOR_STORE_PATH = BASE_DIR/'ChromaDB'
EMBED_MODEL =  HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
# DRIVE_FOLDER_ID =  os.environ['GOOGLE_DRIVE_FOLDER_ID']
DRIVE_API_SCOPES =  ["https://www.googleapis.com/auth/drive.activity.readonly", "https://www.googleapis.com/auth/drive",]
MONITORING_TIME_DELAY  = 10 
GOOGLE_GEMINI_API_KEY = os.environ['GOOGLE_API_KEY']
PARAGRAPH_SPLITTER_EXPRESSION = r'[\n][\s]*[\n][\n\s]*'
GOOGLE_DRIVE_ACTIVITY_PAGE_SIZE = 5

FERNET_KEY = os.environ["FERNET_KEY"].encode() # For encrypt Google drive Access token in server 

### Fast API Auth System Information 
JWT_AUTH_SECRET_KEY = os.environ['JWT_AUTH_SECRET_KEY']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
## One Drive Constant 
ONEDRIVE_SCOPE = ['Files.Read']
ONEDRIVE_LOGIN_EXPIRE_DURATION = 600
TEMP_STORE_PATH = Path('./tmp_au4os42asx4fgj45mz9db4zj5r3xd7ghm/')
GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
ONE_DRIVE_ITEM_ENDPOINT = GRAPH_API_ENDPOINT + r'/me/drive/items'

ONEDRIVE_CREDENTIAL_DIR = BASE_DIR/'CredentialHub'/'ms_credential'
if not ONEDRIVE_CREDENTIAL_DIR.exists():
    ONEDRIVE_CREDENTIAL_DIR.mkdir(parents=True)
    
    
    
GDRIVE_ACCEPT_MIME_TYPES = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
    # 'application/json',
    'text/html',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation'
    'application/pdf', 'text/plain',
]

MS_CLIENT_ID = os.environ['MS_CLIENT_ID']