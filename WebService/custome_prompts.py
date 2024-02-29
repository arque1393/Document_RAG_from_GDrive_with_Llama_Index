from llama_index.core import PromptTemplate
prompt_template_str = ('''As a most efficient Question Answering Engine your job is find answer of the following question from the given Context.
The Context information is provided bellow: \n
---------------------------------------
{context_str}
---------------------------------------\n
Given the context information and not prior knowledge, 

Question : {query_str}\n

Provide answer from the given context only 
'''
)

custom_prompt_template = PromptTemplate(prompt_template_str)