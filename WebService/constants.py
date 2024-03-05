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
DRIVE_FOLDER_ID =  os.environ['GOOGLE_DRIVE_FOLDER_ID']
DRIVE_API_SCOPES = ["https://www.googleapis.com/auth/drive.activity.readonly"]
MONITORING_TIME_DELAY  = 10 
GOOGLE_GEMINI_API_KEY = os.environ['GOOGLE_API_KEY']
PARAGRAPH_SPLITTER_EXPRESSION = r'[\n][\s]*[\n][\n\s]*'




### Fast API Auth System Information 
JWT_AUTH_SECRET_KEY = os.environ['JWT_AUTH_SECRET_KEY']
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
