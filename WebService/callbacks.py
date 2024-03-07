from vector_store import ChromaVectorStoreIndex
from document_processor import process_document
from constants import (VECTOR_STORE_PATH ,
                    GOOGLE_CREDENTIALS_PATH, GOOGLE_GEMINI_API_KEY)
from llama_index.readers.google import GoogleDriveReader
from llama_index.llms.gemini import Gemini
from custome_prompts import custom_prompt_template
from document_processor import process_metadata
from typing import Tuple


def store_data_callback(username:str,collection_name:str)-> callable:
    def callback(file_ids:str):        
        drive_loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH,
                token_path='llama_index_drive_loader/token.json',
                pydrive_creds_path='llama_index_drive_loader/creds.txt')
        chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH/username, collection=collection_name)
        docs = drive_loader.load_data(file_ids=file_ids)
        if not docs:
            raise Exception("No Datas is loaded")        
        try:
            nodes = process_document(docs)
            _ = chroma_index.create_index(nodes=nodes)           
        except Exception as e:
            print('Error occurs in Indexing', e)
            
    return callback 
        
def get_answer(username:str, collection_name:str , question:str ) -> Tuple[str,dict]:
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH/username, collection=collection_name)
   
    index = chroma_index.load_index(persist_dir=VECTOR_STORE_PATH/username, collection_name=collection_name)
    query_engine = index.as_query_engine(llm=Gemini(api_key=GOOGLE_GEMINI_API_KEY))    
    query_engine.update_prompts({"response_synthesizer:text_qa_template": custom_prompt_template})    
    response = query_engine.query(question)
    # print(response.metadata)    
    return (response.response,process_metadata(response.metadata))