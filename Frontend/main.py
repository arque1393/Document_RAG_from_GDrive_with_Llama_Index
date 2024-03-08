import streamlit as st 
from streamlit_extras.switch_page_button import switch_page

from request_manager import create_collection
st.set_page_config(page_title= "Intelegent Document Retriever")
st.title("Home")
st.sidebar.success("Select a page ")

folder_link = st.text_input("Enter Folder Link")

if st.button("Add Folder ID as Collection "):
    response = create_collection(folder_link)
    try : 
        st.success(response['message'])
    except:
        st.error(response['detail'])
if st.button('Ask Question'):
    switch_page('rag')