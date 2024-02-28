from llama_index.core.extractors import (
    TitleExtractor,
    # QuestionsAnsweredExtractor,
)
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import Document
import nest_asyncio
from llama_index.llms.gemini import Gemini 
from llama_index.core.ingestion import IngestionPipeline

nest_asyncio.apply()

def process_document(documents:list[Document]):

    text_splitter = TokenTextSplitter( separator=" ", chunk_size=512, chunk_overlap=128 )
    title_extractor = TitleExtractor(nodes=5, llm= Gemini())
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
    pass