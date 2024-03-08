import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from request_manager import login_req
st.title("Login Page")
username = st.text_input("Username")
password = st.text_input("Password", type="password")
if st.button("Login"):
    status,message = login_req(username,password)
    if status=='success':
        switch_page("main")
    else:
        st.error(message)