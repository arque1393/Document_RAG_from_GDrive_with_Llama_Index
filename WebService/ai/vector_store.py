import chromadb
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.schema import BaseNode
from llama_index.core.embeddings import BaseEmbedding
from llama_index.core import StorageContext, VectorStoreIndex 
from llama_index.vector_stores.chroma import ChromaVectorStore
from WebService.constants import EMBED_MODEL
from llama_index.core.llms.llm import LLM
from typing import Union,Sequence,Optional
from pathlib import Path 


class ChromaVectorStoreIndex(object):
    '''This class is a simple control tool for Vector Store Index using ChromaDB 
    '''
    
    def __init__(self,persist_dir : Union[Path,str], 
                collection:str='default', 
                embed_model:Optional[BaseEmbedding] = None,
                llm: Optional[Union[str, LLM]] = None,
                 **kwargs):    

        _persist_dir:str = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()
        self.chroma_client = chromadb.PersistentClient(path=_persist_dir)
        self.chroma_collection = self.chroma_client.get_or_create_collection(collection)
        self.chroma_vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)   
        self.llm = llm 
        if embed_model :
            self.embed_model = embed_model
        else :
            self.embed_model = EMBED_MODEL
        self.kwargs = kwargs
        

    def create_index(self,nodes:Sequence[BaseNode]):
        self.kwargs['nodes']=nodes
        self.kwargs['embed_model'] = self.embed_model
        self.kwargs['storage_context']=StorageContext.from_defaults(
                vector_store=self.chroma_vector_store) 
        self.__index = VectorStoreIndex(**self.kwargs)
        return self.__index
    
    def load_index(self, persist_dir: Optional[Union[Path,str]]=None, 
                            collection_name:Optional[str]=None,embed_model:Optional[BaseEmbedding]=None) :
        if persist_dir :
            _persist_dir:str = persist_dir if type(persist_dir)==str else persist_dir.resolve().__str__()  
            self.chroma_client = chromadb.PersistentClient(path=_persist_dir)
        if collection_name :
            self.chroma_collection = self.chroma_client.get_or_create_collection(collection_name)
        if persist_dir and collection_name:
            self.chroma_vector_store = ChromaVectorStore(chroma_collection=self.chroma_collection)            
        if  embed_model:
            self.embed_model = embed_model
            
        self.__index = VectorStoreIndex.from_vector_store(
            self.chroma_vector_store,
            embed_model=self.embed_model)
        return self.__index

        
    def get_retriever(self, llm: Optional[Union[str, LLM]] = None,**kwargs):
        if not llm: llm = self.llm
        return self.__index.as_retriever(llm = llm)
    
    def get_query_engine (self, llm: Optional[Union[str, LLM]] = None,**kwargs):
        if not llm: llm = self.llm
        return self.__index.as_query_engine(llm = llm)
        
    def get_chat_engine (self, llm: Optional[Union[str, LLM]] = None,**kwargs):
        if not llm: llm = self.llm
        return self.__index.as_chat_engine(llm = llm)
        
    




