import streamlit as st
import requests

# Page 1: Login / Signup
def login_signup():
    st.title("Login / Signup")

    # User input fields
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    # Sign up function
    def signup(username, email, password):
        signup_data = {"username": username, "email":email, "password": password}
        response = requests.post("http://127.0.0.1:8000/user", json=signup_data)
        return response.json()

    # Login function
    def login(username, password):
        url = 'http://127.0.0.1:8000/token'
        headers = {'accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded'}
        login_data = {"username": username, "password": password}
        response = requests.post(url, headers=headers, data=login_data)
        return response.json()

    # Login or Signup
    if st.button("Login"):
        login_response = login(username, password)
        print(login_response)
        # if login_response.get("success"):
        #     st.success("Login successful!")
            # Navigate to next page
        st.rerun()
    elif st.button("Signup"):
        signup_response = signup(username, password)
        if signup_response.get("success"):
            st.success("Signup successful!")
            # Navigate to next page
            st.rerun()

# Page 2: Navigation bar with Two pages
def navigation_bar():
    st.title("Navigation Bar")
    page = st.sidebar.selectbox("Select a page", ["Input", "Input and Output"])

    if page == "Input":
        input_page()
    elif page == "Input and Output":
        input_output_page()

# Page 2.1: Input field and submit button
def input_page():
    st.header("Input Page")
    input_text = st.text_input("Enter some text")
    if st.button("Submit"):
        st.success("Submitted: {}".format(input_text))

# Page 2.2: Input field, submit button, and output field
def input_output_page():
    st.header("Input and Output Page")
    input_text = st.text_input("Enter some text")
    if st.button("Submit"):
        output_text = input_text.upper()
        st.success("Output: {}".format(output_text))

# Main function to run the app
def main():
    page = st.query_params.get("page", ["login_signup"])[0]

    if page == "login_signup":
        login_signup()
    elif page == "navigation_bar":
        navigation_bar()

if __name__ == "__main__":
    main()
