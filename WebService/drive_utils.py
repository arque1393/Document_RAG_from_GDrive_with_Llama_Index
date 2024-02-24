from llama_index.readers.google import GoogleDriveReader
from constants import GOOGLE_CREDENTIALS_PATH
loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH)

def load_data_from_drive_folder(folder_id: str):
    docs = loader.load_data(folder_id=folder_id)
    if not docs :
        raise Exception("Content Load Error","No content is loaded")
        
    return docs

