from constants import DRIVE_FOLDER_ID
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.gemini import Gemini

from vector_store import ChromaVectorStoreIndex
from document_processor import process_document, process_metadata
from constants import (VECTOR_STORE_PATH ,
        GOOGLE_CREDENTIALS_PATH,GOOGLE_GEMINI_API_KEY)
from llama_index.readers.google import GoogleDriveReader
from drive_utils import watch_drive_load_data
import gradio as gr
from custome_prompts import custom_prompt_template
# from interface import WebInterface
import threading
import time 

if __name__ == '__main__':
    
    def web_interface_output(query:str,collection:str):
        chroma_index = ChromaVectorStoreIndex(persist_dir=VECTOR_STORE_PATH, collection=collection)
        index = chroma_index.load_index()
        query_engine = index.as_query_engine(llm=Gemini(api_key=GOOGLE_GEMINI_API_KEY))
        query_engine.update_prompts({"response_synthesizer:text_qa_template": custom_prompt_template})
        response = query_engine.query(query)
        return (response.response, process_metadata(response.metadata))

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
            index = chroma_index.create_index(nodes=nodes)           
        except Exception as e:
            print('Error occurs in Indexing', e)
        
        
        
        
    ## Define Gradio Interface 
    
    question_input = gr.Textbox(label="Enter your query")
    output_text = gr.Textbox(label="Answer")
    output_text_metadata = gr.Textbox(label="Resource")
    select_folder = gr.Dropdown(DRIVE_FOLDER_ID)
    interface = gr.Interface(
        fn=web_interface_output,
        inputs=[question_input,select_folder],
        outputs=[output_text,output_text_metadata],
        title="Question-Answer Interface",
        description="Enter your question and get answers in both text and table format."
    )

    def drive_watcher_thread ():
        watch_drive_load_data(DRIVE_FOLDER_ID[0], store_data_callback)

    def drive_watcher_thread_2 ():
        watch_drive_load_data(DRIVE_FOLDER_ID[1], store_data_callback)


    
    
    
    def web_interface_thread ():
        # interface = WebInterface(web_interface_output)
        # while True :
        #     if flag_to_control_web_thread:
        #         break
        time.sleep(30)
        interface.launch()   
        
        
    thread1 = threading.Thread(target=drive_watcher_thread)    
    thread2 = threading.Thread(target=drive_watcher_thread_2)    
    thread3 = threading.Thread(target=web_interface_thread)    
    
    thread1.start()
    thread2.start()
    thread3.start()
    

    thread1.join()
    thread2.join()

    
