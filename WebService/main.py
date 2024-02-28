from constants import DRIVE_FOLDER_ID
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.gemini import Gemini

from vector_store import ChromaVectorStoreIndex
from constants import VECTOR_STORE_PATH ,GOOGLE_CREDENTIALS_PATH
from llama_index.readers.google import GoogleDriveReader
from drive_utils import watch_drive_load_data
import gradio as gr

# from interface import WebInterface
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
            print("*******************")
            index = self.chroma_index.create_index(nodes=nodes)
            
            # Experiment 
            query_engine = index.as_query_engine(llm=Gemini())
            print(query_engine.query("What is Self Attention ?").response)
            
        except:
            print("No new data found")
        
        
if __name__ == '__main__':
    chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection='Set1')
    drive_retriever = RAG_Drive_retriever(chroma_index)
    def web_interface_output(query:str):
        chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection='Set1')
        print("\n\**********\n************\n*************\n\n")
        index = chroma_index.load_index()
        query_engine = index.as_query_engine(llm=Gemini())
        print(query)        
        response = query_engine.query(query)
        print(response.response, response.metadata, 'ff')
        return (response.response, response.metadata)
    
    question_input = gr.Textbox(label="Enter your query")
    output_text = gr.Textbox(label="Answer")
    output_text_metadata = gr.Textbox(label="Resource")
    interface = gr.Interface(
        fn=web_interface_output,
        inputs=question_input,
        outputs=[output_text,output_text_metadata],
        title="Question-Answer Interface",
        description="Enter your question and get answers in both text and table format."
    )

    def drive_watcher_thread ():
        watch_drive_load_data(DRIVE_FOLDER_ID, drive_retriever.store_data)
        

    
    
    def web_interface_thread ():
        # interface = WebInterface(web_interface_output)
        time.sleep(10)
        interface.launch()   
        
        
    thread1 = threading.Thread(target=drive_watcher_thread)    
    thread2 = threading.Thread(target=web_interface_thread)    
    thread1.start()
    thread2.start()
    
    
thread1.join()
thread2.join()
    # while True :
    #     print("server is running")
    #     query = input('Ask your Query : ')
    #     print(query_engine.query(query))
    #     # time.sleep(100)


    
