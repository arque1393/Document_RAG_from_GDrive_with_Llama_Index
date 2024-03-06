from vector_store import ChromaVectorStoreIndex
from document_processor import process_document
from constants import (VECTOR_STORE_PATH ,GOOGLE_CREDENTIALS_PATH)
from llama_index.readers.google import GoogleDriveReader

def store_data_callback(file_ids,collection_name):        
    drive_loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH,
            token_path='llama_index_drive_loader/token.json',
            pydrive_creds_path='llama_index_drive_loader/creds.txt')
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection=collection_name)
    docs = drive_loader.load_data(file_ids=file_ids)
    if not docs:
        raise Exception("No Datas is loaded")        
    try:
        nodes = process_document(docs)
        _ = chroma_index.create_index(nodes=nodes)           
    except Exception as e:
        print('Error occurs in Indexing', e)