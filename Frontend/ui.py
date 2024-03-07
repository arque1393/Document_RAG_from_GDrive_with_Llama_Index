selected_var = None
import tkinter as tk
from tkinter import ttk

from tkinter import messagebox
import requests
import json

def get_token ():
    with open('token.b','rb')as f:
        token = f.read()
        return json.loads(token.decode())
        
def save_token(token):
    with open('token.b','wb')as f:
        f.write(json.dumps(token).encode())
        
def send_query(question):
    global selected_var
    token = get_token()
    access_token = token['access_token']
    
    url = 'http://127.0.0.1:8000/user/query'
    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    data = {
        "collection_name": str(selected_var),
        "question":str(question)
    }
    response = requests.post(url, headers=headers, json=data)
    return  response.json()
    
    


def login():
    # Function to handle login button click
    def handle_login():
        # Retrieve login credentials
        username = username_entry.get()
        password = password_entry.get()
        url = 'http://127.0.0.1:8000/token'
        headers = {'accept': 'application/json','Content-Type': 'application/x-www-form-urlencoded'}
        login_data = {"username": username, "password": password}
        response = requests.post(url, headers=headers, data=login_data)
        save_token(response.json())
        messagebox.showinfo("Sign Up", "Signed up successfully!")
        login_window.destroy()        
        after_auth()
        initial_frame.destroy()
    # Create login window
    login_window = tk.Toplevel(root)
    login_window.title("Login")
    username = tk.Label(login_window, text="Username:")
    username.grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(login_window, width=30)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    password_label = tk.Label(login_window, text="Password:")
    password_label.grid(row=1, column=0, padx=10, pady=5)
    password_entry = tk.Entry(login_window, show="*", width=30)
    password_entry.grid(row=1, column=1, padx=10, pady=5)
    login_button = tk.Button(login_window, text="Login", command=handle_login)
    login_button.grid(row=2, column=0, columnspan=2, pady=10)
    
def signup():
    # Function to handle signup button click
    def handle_signup():
        # Retrieve signup credentials
        username = username_entry.get()
        email = email_entry.get()
        password = password_entry.get()

        # Code to register user can be implemented here
        # For simplicity, let's just show a messagebox
        messagebox.showinfo("Sign Up", f"Signed up successfully!\nUsername: {username}\nEmail: {email}\nPassword: {password}")
        signup_window.destroy()

    # Create signup window
    signup_window = tk.Toplevel(root)
    signup_window.title("Sign Up")

    username_label = tk.Label(signup_window, text="Username:")
    username_label.grid(row=0, column=0, padx=10, pady=5)
    username_entry = tk.Entry(signup_window, width=30)
    username_entry.grid(row=0, column=1, padx=10, pady=5)
    email_label = tk.Label(signup_window, text="Email:")
    email_label.grid(row=1, column=0, padx=10, pady=5)
    email_entry = tk.Entry(signup_window, width=30)
    email_entry.grid(row=1, column=1, padx=10, pady=5)
    password_label = tk.Label(signup_window, text="Password:")
    password_label.grid(row=2, column=0, padx=10, pady=5)
    password_entry = tk.Entry(signup_window, show="*", width=30)
    password_entry.grid(row=2, column=1, padx=10, pady=5)
    signup_button = tk.Button(signup_window, text="Sign Up", command=handle_signup)
    signup_button.grid(row=3, column=0, columnspan=2, pady=10)

# Create main window
root = tk.Tk()
root.title("My App")

# Create initial window with login and signup buttons
initial_frame = tk.Frame(root)
initial_frame.pack(padx=20, pady=20)
title_label = tk.Label(initial_frame, text="Welcome to My App", font=("Helvetica", 16))
title_label.grid(row=0, column=0, columnspan=2, pady=10)
login_button = tk.Button(initial_frame, text="Login", width=10, command=login)
login_button.grid(row=1, column=0, padx=5)
signup_button = tk.Button(initial_frame, text="Sign Up", width=10, command=signup)
signup_button.grid(row=1, column=1, padx=5)


def after_auth():
    
    
    def on_submit():
        query = query_entry.get()
        response = send_query(query,)
        output_label.config(text=str(response))
        
    def selection_changed(event):
        global selected_var
        selected_var = listbox.get(tk.ACTIVE)
    
    def get_collection():
        token = get_token()
        access_token = token['access_token']
        url = 'http://127.0.0.1:8000/user/collections'
        headers = {
            'accept': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(url, headers=headers)
        print(type(response.json()))
        return [collection['collection_name'] for collection in response.json()]
    
    authenticated_frame = tk.Frame(root)
    authenticated_frame.pack(padx=20,pady=20)
    question_label = tk.Label(authenticated_frame, text="Welcome to My App", font=("Helvetica", 12))
    question_label.grid(row=0, column=0, columnspan=2, pady=10)
    query_entry = tk.Entry(authenticated_frame, width=30)
    query_entry.grid(row=1,column=0, padx=5)
    output_label = tk.Label(authenticated_frame, text="Output",width=150, font=("Helvetica", 10),wraplength=1000)
    output_label.grid(row=4, column=0, padx=5)
    
    listbox = tk.Listbox(authenticated_frame)
    listbox.grid(row=3, column=0, padx=5)
    for item in get_collection():
        listbox.insert(tk.END, item)
    listbox.bind("<<ListboxSelect>>", selection_changed)
    
    submit_button = tk.Button(authenticated_frame, text="Submit", width=50, command=on_submit)
    submit_button.grid(row=2, column=0, padx=5)
    
    
root.mainloop()
