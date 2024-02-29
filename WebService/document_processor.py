from llama_index.core.extractors import (
    TitleExtractor,
    # QuestionsAnsweredExtractor,
)
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import Document
import nest_asyncio
from llama_index.llms.gemini import Gemini 
from llama_index.core.ingestion import IngestionPipeline
GOOGLE_GEMINI_API_KEY = 'AIzaSyCyHIeutwgqev35okEgy6b913Zmfq3RqnA'
nest_asyncio.apply()

def process_document(documents:list[Document]):
    for document in documents :
        document
    text_splitter = TokenTextSplitter( separator=" ", chunk_size=512, chunk_overlap=128 )
    title_extractor = TitleExtractor(nodes=5, llm= Gemini(api_key=GOOGLE_GEMINI_API_KEY))
    pipeline = IngestionPipeline(
        transformations=[text_splitter, title_extractor]
    )
    nodes = pipeline.run(
        documents=documents,
        in_place=True,
        show_progress=True,
    )
    return nodes


def process_metadata(metadata:dict):
    extractor_list = ['author','file name','created at', 'modified at', 'page_label', 'document_title' ] 
    
    extracted_metadata={}
    for key in extractor_list :
        try: extracted_metadata[key] = metadata[key]
        except: extracted_metadata[key] = 'Not Applicable'
    return extracted_metadata
        

# if __name__ == '__main__':
#     from llama_index.readers.google import GoogleDriveReader
    
#     drive_loader = GoogleDriveReader(credentials_path='../Google_Credentials/PROJECT_ID.json',
#                 token_path='llama_index_drive_loader/token.json',
#                 pydrive_creds_path='llama_index_drive_loader/creds.txt')
#     docs = drive_loader.load_data(file_ids=['1ZUiPV7C-ey2NT3hotbXtj1BfVW-5DPKY'])
#     print(len(docs))
    