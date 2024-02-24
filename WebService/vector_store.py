import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore, BaseNode
from llama_index.embeddings import BaseEmbedding
from llama_index.core import StorageContext, VectorStoreIndex 
from llama_index.vector_stores.chroma import ChromaVectorStore
from constants import EMBED_MODEL

from typing import Union,Sequence,Optional
from pathlib import Path 


class ChromaVectorStoreIndex(VectorStoreIndex):
    '''This class is a simple control tool for ChromaDB 
    '''
    
    def __init__(self,nodes:Sequence[BaseNode],persist_dir : Union[Path,str],collection:str='default',**kwargs):          
        persist_dir = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()
        self.chroma_client = chromadb.PersistentClient(path=persist_dir)
        self.chroma_collection = self.client.get_or_create_collection(collection)
        self.chroma_vector_store = ChromaVectorStore(chroma_collection=self.collection)    
        if kwargs['embed_model'] is None :
            kwargs['embed_model'] = EMBED_MODEL
        kwargs['nodes']=nodes
        kwargs['storage_context']=StorageContext.from_defaults(
                vector_store=self.chroma_vector_store) 
        
        super(VectorStoreIndex, self).__init__(**kwargs)
        
    @classmethod   
    def load_vector_store(persist_dir:Union[Path,str], collection_name:str,embed_model:Optional[BaseEmbedding]=None) :
        persist_dir = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()        
        client = chromadb.PersistentClient(path=persist_dir)
        chroma_collection = client.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        if not embed_model:
            embed_model = EMBED_MODEL
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model)
        return index 

# lOADING TEXT AFTER SELECT 







