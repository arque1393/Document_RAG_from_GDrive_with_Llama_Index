# Here are some Global Constants variables 
from pathlib import Path 
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os
BASE_DIR = Path(__file__).resolve().parent
## Please Change the Path according to your Google Credential Json
GOOGLE_CREDENTIALS_PATH = BASE_DIR.parent/'Google_Credentials'/'PROJECT_ID.json'
GOOGLE_CLIENT_SECRET = BASE_DIR.parent/'Google_Credentials'/'CLIENT_SECRET.json'
VECTOR_STORE_PATH = BASE_DIR/'ChromaDB'
EMBED_MODEL =  HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
DRIVE_FOLDER_ID = '11AL-KYS70DaDqAqAMVFTeFH-GTCE9f44'
DRIVE_API_SCOPES = ["https://www.googleapis.com/auth/drive.activity.readonly"]
MONITORING_TIME_DELAY  = 10 
GOOGLE_GEMINI_API_KEY = os.environ['GOOGLE_API_KEY']
PARAGRAPH_SPLITTER_EXPRESSION = r'[\n][\s]*[\n][\n\s]*'

# MIME_TYPES = [  'text/plain','application/vnd.openxmlformats-officedocument.wordprocessingml.document',
#                 'application/pdf','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
#                 'text/csv','text/tab-separated-values','application/vnd.openxmlformats-officedocument.presentationml.presentation',
#                 'application/vnd.google-apps.script+json'
#             ]

