from WebService.ai.vector_store import ChromaVectorStoreIndex
from WebService.constants import (VECTOR_STORE_PATH ,GOOGLE_CREDENTIALS_PATH, GOOGLE_GEMINI_API_KEY)
from llama_index.readers.google import GoogleDriveReader
from llama_index.llms.gemini import Gemini
from WebService.ai.custome_prompts import custom_prompt_template
from WebService.ai.document_processor import process_metadata,process_document
from typing import Tuple
from WebService.utils.drive import OneDriveReader

def store_data_callback(username:str)-> callable:
    """This Function create a callback function to read google Drive Files and store data in vectoe database using ChromaVectorStoreIndex.
    Using the username this function definite to use specific user
    """    
    def callback(file_ids:str,collection_name:str):    
        """Read google Drive Files and Store in Vector Store """    
        drive_loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH,
                token_path='llama_index_drive_loader/token.json',
                pydrive_creds_path='llama_index_drive_loader/creds.txt')
        chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH/username, collection=collection_name)
        docs = drive_loader.load_data(file_ids=file_ids)
        if not docs:
            raise Exception("No Datas is loaded")        
        try:
            nodes = process_document(docs,"Google Drive")
            _ = chroma_index.create_index(nodes=nodes)           
        except Exception as e:
            print('Error occurs in Indexing', e)
            
    return callback 


        
def get_answer(username:str, collection_name:str , question:str ) -> Tuple[str,dict]:
    """Ask Query using LLM and return response and Processed metadata """
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH/username, collection=collection_name)
   
    index = chroma_index.load_index(persist_dir=VECTOR_STORE_PATH/username, collection_name=collection_name)
    query_engine = index.as_query_engine(llm=Gemini(api_key=GOOGLE_GEMINI_API_KEY))    
    query_engine.update_prompts({"response_synthesizer:text_qa_template": custom_prompt_template})    
    response = query_engine.query(question)
    # print(response.metadata)    
    return (response.response,process_metadata(response.metadata))





def store_data_from_onedrive(username:str, access_token:str, file_list=None, folder_id = None):
    """Read google Drive Files and Store in Vector Store """    
    reader = OneDriveReader(username=username, access_token=access_token)
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH/username, collection=username)
    if file_list:
        docs = reader.load_data(file_ids=file_list)
    elif folder_id:
        docs = reader.load_data(folder_id=folder_id)
    else:
        docs = reader.load_data(folder_id='root')
    if not docs:
        raise Exception("No Data is loaded")        
    try:
        nodes = process_document(docs, "One Drive")
        _ = chroma_index.create_index(nodes=nodes)           
    except Exception as e:
        print('Error occurs in Indexing', e)