from llama_index.core.extractors import (
    TitleExtractor,
    # QuestionsAnsweredExtractor,
)
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import Document
import nest_asyncio
from llama_index.llms.gemini import Gemini 
from llama_index.core.ingestion import IngestionPipeline

from constants import GOOGLE_GEMINI_API_KEY

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
    extracted_metadata=''
    metadata=iter(metadata.values()).__next__()
    for key in extractor_list :
        try: 
            extracted_metadata = extracted_metadata + key + " :: " + metadata[key]+'\n'
        except: 
            continue
    return extracted_metadata
