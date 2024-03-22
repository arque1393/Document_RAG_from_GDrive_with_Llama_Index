import streamlit as st 
from streamlit_extras.switch_page_button import switch_page
from request_manager import get_collections,send_query
from request_manager import logout
from request_manager import create_collection
from request_manager import connect_to_google , connect_to_onedrive
import json

st.set_page_config(page_title= "Intelegent Document Retriever")
st.title("Home Page")



st.subheader("Question Answer")

question = st.text_input("Enter Your Question")
st.write("Click to Get Collection List to View Your Folder Collection ")

        
button_google = st.sidebar.button("Connect to Google Drive")
button_one_drive = st.sidebar.button("Connect to One Drive") 
button_one_drive_connection_verification   = st.sidebar.button("Verify connection") 
read_one_derive = st.sidebar.button("Read _One Drive Data")  

if button_google :
    res = connect_to_google()
    try: 
        mes  = res['message']
        st.success(mes)
    except :
        mes  = res['detail']
        st.error(mes)
        
if button_one_drive:
    res = connect_to_onedrive()
    try: 
        # st.write(res)
        code  = res['user_code']
        st.sidebar.write(f"Code is {code}")
    except : 
        pass
if button_one_drive_connection_verification:
    try :
        res = connect_to_onedrive('/verify')
        mes  = res['message']
        st.success(mes)
    except:
        mes  = res['detail']
        st.error(mes)


if read_one_derive :
    res = connect_to_onedrive('/read')
    try:
        st.success(res['message'])
    except:
        st.error(res['detail'])
if st.button("Submit Query"):
    try:
        response = send_query(question)
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