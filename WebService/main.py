from constants import DRIVE_FOLDER_ID
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.gemini import Gemini

from vector_store import ChromaVectorStoreIndex
from constants import VECTOR_STORE_PATH ,GOOGLE_CREDENTIALS_PATH
from llama_index.readers.google import GoogleDriveReader
from drive_utils import watch_drive_load_data
import threading
import time 
class RAG_Drive_retriever():
    def __init__(self, vector_store_index:ChromaVectorStoreIndex) -> None:
        self.drive_loader = GoogleDriveReader(credentials_path=GOOGLE_CREDENTIALS_PATH,
                token_path='llama_index_drive_loader/token.json',
                pydrive_creds_path='llama_index_drive_loader/creds.txt')
        self.chroma_index = vector_store_index
        
    def load_data(self, file_ids:list[str]):
        docs = self.drive_loader.load_data(file_ids=file_ids)
        if docs:
            return docs
        else:
            raise Exception("No Datas is loaded")
        
    def store_data(self,list_file_ids):
        try:
            documents = self.load_data(list_file_ids)    
            node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)
            nodes = node_parser.get_nodes_from_documents(
                documents, show_progress=False
            )
            self.chroma_index.create_index(nodes=nodes)
        except:
            print("No new data found")
        
        
if __name__ == '__main__':
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection='Set1')
    drive_retriever = RAG_Drive_retriever(chroma_index)
    

    def drive_watcher_thread ():
        watch_drive_load_data(DRIVE_FOLDER_ID, drive_retriever.store_data)
        
    thread1 = threading.Thread(target=drive_watcher_thread)    
    thread1.start()
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection='Set1')
    index = chroma_index.load_index()
    query_engine = index.as_query_engine(llm=Gemini())
    
    
    
    while True :
        print("server is running")
        # query = input('Ask your Query : ')
        # print(query_engine.query(query))
        time.sleep(100)


    
