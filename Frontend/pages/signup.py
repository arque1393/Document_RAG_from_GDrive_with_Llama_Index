import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from request_manager import signup_req


st.title("Login Page")
username = st.text_input("Username")
email = st.text_input("Email")
password = st.text_input("Password", type="password")
if st.button("Signup"):
    status,message = signup_req(str(username),str(email),str(password))
    if status=='success':
        switch_page("main")
    else:
        st.error(message)