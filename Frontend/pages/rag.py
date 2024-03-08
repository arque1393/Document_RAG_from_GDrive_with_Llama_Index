import streamlit as st
from streamlit_option_menu import option_menu
from request_manager import get_collections,send_query
st.title("RAG Page")

question = st.text_input("Enter Your Question")
st.write("Click to Get Collection List to View Your Folder Collection ")
if st.button("Get Collection List"):
    collection_list = get_collections()
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
    response = send_query(question,collection_name)
    answer = response['answer']
    metadata =  response['metadata']
    st.subheader("Answer")
    st.write( answer )
    st.subheader("Metadata")
    st.write( metadata )
    




