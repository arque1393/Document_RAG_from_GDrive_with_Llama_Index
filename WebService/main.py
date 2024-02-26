from constants import DRIVE_FOLDER_ID
from drive_utils import load_data_from_drive_folder
from llama_index.core.node_parser import SentenceSplitter

from vector_store import ChromaVectorStoreIndex
from constants import VECTOR_STORE_PATH 


if __name__ == '__main__':
    documents = load_data_from_drive_folder(DRIVE_FOLDER_ID)    
    node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

    nodes = node_parser.get_nodes_from_documents(
        documents, show_progress=False
    )
    # print(nodes)
    chroma_index = ChromaVectorStoreIndex(nodes,persist_dir=VECTOR_STORE_PATH, collection='Set1')
    index = chroma_index.get_chroma_index()
    # print("****************************************************",index)
    index2 = chroma_index.load_vector_store(persist_dir=VECTOR_STORE_PATH, collection_name ='Set1')
    print(index2)