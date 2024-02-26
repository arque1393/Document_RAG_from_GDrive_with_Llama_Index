import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.schema import BaseNode
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core import StorageContext, VectorStoreIndex 
from llama_index.vector_stores.chroma import ChromaVectorStore
from constants import EMBED_MODEL
from llama_index.core.llms.llm import LLM
from typing import Union,Sequence,Optional
from pathlib import Path 


class ChromaVectorStoreIndex(object):
    '''This class is a simple control tool for ChromaDB 
    '''
    
    def __init__(self,nodes:Sequence[BaseNode],persist_dir : Union[Path,str], 
                collection:str='default', llm: Optional[Union[str, LLM]] = None,
                 **kwargs):    

        _persist_dir:str = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()
        self.chroma_client = chromadb.PersistentClient(path=_persist_dir)
        self.chroma_collection = self.chroma_client.get_or_create_collection(collection)
        self.chroma_vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)   
        self.llm = llm 
        if 'embed_model' not in kwargs :
            kwargs['embed_model'] = EMBED_MODEL
        kwargs['nodes']=nodes
        kwargs['storage_context']=StorageContext.from_defaults(
                vector_store=self.chroma_vector_store) 
        print(_persist_dir)
        self.__index = VectorStoreIndex(**kwargs)
    def get_chroma_index(self):
        return self.__index
    
    def load_vector_store(self, persist_dir:Union[Path,str], 
                            collection_name:str,embed_model:Optional[BaseEmbedding]=None) :
        print("Create create_index_from_documents call Chroma Vector Store")
        
        _persist_dir:str = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()        
        client = chromadb.PersistentClient(path=_persist_dir)
        chroma_collection = client.get_or_create_collection(collection_name)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        if not embed_model:
            embed_model = EMBED_MODEL
        index =VectorStoreIndex.from_vector_store(
            vector_store,
            embed_model=embed_model)
        self.__index = index
        
    def get_retriever(self, llm: Optional[Union[str, LLM]] = None):
        if not llm: llm = self.llm
        return self.__index.as_retriever(llm = llm)
    
    def get_query_engine (self, llm: Optional[Union[str, LLM]] = None):
        if not llm: llm = self.llm
        return self.__index.as_query_engine(llm = llm)
        
    def get_chat_engine (self, llm: Optional[Union[str, LLM]] = None):
        if not llm: llm = self.llm
        return self.__index.as_chat_engine(llm = llm)
        
    
# lOADING TEXT AFTER SELECT 




