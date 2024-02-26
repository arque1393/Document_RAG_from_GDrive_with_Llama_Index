# Here are some Global Constants variables 
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.gemini import Gemini 
from pathlib import Path 

BASE_DIR = Path(__file__).resolve().parent
## Please Change the Path according to your Google Credential Json
GOOGLE_CREDENTIALS_PATH = BASE_DIR.parent/'Google_Credentials'/'promactprojecttask4-46c0f330aee7.json'
GOOGLE_CLIENT_SECRET = BASE_DIR.parent/'Google_Credentials'/'client_secret_944885290760-eol8kggkm9kv1bgmlpvisr619v2mk4ul.apps.googleusercontent.com.json'

VECTOR_STORE_PATH = BASE_DIR/'ChromaDB'

LLM = Gemini()
EMBED_MODEL =  HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
DRIVE_FOLDER_ID = '1sLmLETXRAUA1NAoJDf6TxnJ21SJiXzQ3';
DRIVE_API_SCOPES = ["https://www.googleapis.com/auth/drive.activity.readonly"]
