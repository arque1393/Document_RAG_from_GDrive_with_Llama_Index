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