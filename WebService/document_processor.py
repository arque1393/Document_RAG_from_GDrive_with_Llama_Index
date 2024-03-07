import re 
from llama_index.core.extractors import TitleExtractor
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import Document
import nest_asyncio
from llama_index.core.ingestion import IngestionPipeline
from llama_index.llms.gemini import Gemini 
from llama_index.core import Document 
from constants import GOOGLE_GEMINI_API_KEY, PARAGRAPH_SPLITTER_EXPRESSION

nest_asyncio.apply()

def process_document(documents:list[Document]):
    """It is a simple document processor that do following Tasks :
        1. Divide the text into Paragraph and extract paragraph No and store in metadata for future 
        2. Divide Documents into smaller chunks and store into Nodes. 
        3. Extract Title using Node Content. Use Llama Index's Title Extractors 
    Args:
        documents (list[Document]): Document that return by the GoogleDriveReader class or any other document reader class 
    Returns:
        List[Node]: Return Node for Embedding and Indexing 
    """
    new_list_document: list[Document] = []
    for document in documents :
        paragraph_count = 1
        text = document.text
        metadata = document.metadata
        splitted_text = re.split(PARAGRAPH_SPLITTER_EXPRESSION,text)
        for text in splitted_text:
            metadata['paragraph_no'] = paragraph_count
            doc = Document(text=text, metadata= metadata)
            new_list_document.append(doc)
            paragraph_count +=1 
    text_splitter = TokenTextSplitter( separator=" ", chunk_size=1024, chunk_overlap=0 )
    title_extractor = TitleExtractor(nodes=10, llm= Gemini(api_key=GOOGLE_GEMINI_API_KEY))
    pipeline = IngestionPipeline(
        transformations=[text_splitter, title_extractor]
    )
    nodes = pipeline.run(
        documents=new_list_document,
        show_progress=False,
    )
    return nodes


def process_metadata(metadata:dict):
    """After getting response from the VectorStoreInddex class, it extract required Metadata to display     
    Args:
        metadata (dict): This should be the total metadata dictionary that Index object return as response         
    Returns:
        _type_: Required Metadata 
    """
    if not metadata: return "No Metadata found"
    extractor_list = ['author','file name', 'document_title', 'page_label','paragraph_no','created at', 'modified at'] 
    extracted_metadata=''
    metadata=iter(metadata.values()).__next__()
    for key in extractor_list :
        try: 
            extracted_metadata = extracted_metadata + key + f" :  {metadata[key]}"+'\n'
        except: 
            continue
    return extracted_metadata
