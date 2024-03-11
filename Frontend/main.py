import streamlit as st 
from streamlit_extras.switch_page_button import switch_page
from request_manager import get_collections,send_query
from request_manager import logout
from request_manager import create_collection

import json

st.set_page_config(page_title= "Intelegent Document Retriever")
st.title("Home Page")

st.subheader("Create Collection ")

folder_link = st.text_input("Enter Folder Link")

if st.button("Add Folder ID as Collection "):
    try:
        response = create_collection(folder_link)
    except Exception as e: 
        st.error(f'{e}')
        response = None
    if response:
        try : 
            st.success(response['message'])
        except:
            st.error(response['detail'])




st.subheader("Question Answer")

question = st.text_input("Enter Your Question")
st.write("Click to Get Collection List to View Your Folder Collection ")
if st.button("Get Collection List"):
    try:
        collection_list = get_collections()
    except Exception as e:
        st.error(f'{e}')
        collection_list = None
    if collection_list:
        st.write("-"*80)
        st.write("Collection List")
        if collection_list:
            for collection in collection_list :
                st.write(collection)
            st.write("-"*80)
        else : 
            st.write("No Collection is available Create new one")
        
    
collection_name = st.text_input("Enter Collection Name")


if st.button("Submit Query"):
    st.write("Selected Collection ", collection_name )
    try:
        response = send_query(question,collection_name)
    except Exception as e:
        st.error(f'{e}')
        response = None
    if response:
        answer = response['answer']
        metadata =  response['metadata']
        st.subheader("Answer")
        st.write( answer, bg="#f0f0f0")
        st.subheader("Metadata")
        st.write(metadata, bg="#f0f0f0")


# switch_page('rag')
if st.button('Logout'):
    logout()
    switch_page('login')