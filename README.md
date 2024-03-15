
# **Title** :: Intelligent Document Finder with Llama Index 

## Project Information and Overview 

### Demonstration Video Link 
- Previous Task Video 
    1. Main Video Link https://1drv.ms/u/s!Aj2Nbw_0FL8HibtIga-xfVH0gXEB9g?e=yNsozX
    2. Important Additional Information Video  https://1drv.ms/u/s!Aj2Nbw_0FL8HibtHaAfhj89bXEq0xA?e=lfcmJ8
- New Update Task's Video 
    - https://1drv.ms/u/s!Aj2Nbw_0FL8HjagB_ZtTmnP9-OpWOg?e=XsALLn

### Features : 
1. Multi User System : Application can handle multiple user with Proper Security 
2. Security Feature : 
    - JWT Authentication - Token base System 
3. One user can deal with Multiple Google Drive Folder. Application Store Drive Folders as Collection. It gives select option to chose folder name for Question Answers  

4. Automatic Retrieve data from Google Drive folders.
    - Once Folder Link uploaded in the Software, system will check for all folders or collection in certain time interval if changes occurs on selected Google Drive folders. If occurs then it decode that and read newly created or updated files from the Google Drive and **store** all the data in a vector database for future search.
    - As Vector Database ```ChromaDB``` has been used 
5. Automatic observation of Google Drive folders only works on active users.
6. Retrieve any text-based document files 
    - System is able to retrieve any kind of text information files Ex. Documents, PDF, PPT, HTML, Markdown, etc.
    - Using ```llama_index.readers.google.GoogleDriveReader``` to load all document from the selected Google Drive folder 
8. Preprocessing and Vector Store Indexing :
    - Index all the retrieved data by making few pre-processes like Title Extraction, Paragraph Extraction, etc. 
9.  Google's Gemini Model as LLM to answer the Query 
10. Answer content is only limited to the selected specific folder name or collection name 

### Solution Process Steps:
1. Create Google Drive Credential and Service Account 
2. Activate Google Drive API Service 
2. Activate Google Drive Activity API Service 
3. Using  OAuth Implement FastAPI Authentication System 
    - Create JWT Auth Service 
    - Create User and Collection Table
    - Create Different Endpoints (End points are mention bellow)

5. Implement Google Drive Monitoring System 
    - Using User and Collection Database Table running a loop while user is active  
    - Requesting for activity Google Drive to fetch data during certain time intervals for all collection of the user
    - Checking Changes are available or not 
    - If available read files that are changed 
    - This loop is running the background task of FastAPI for each User while they are active 
4. Process data to extract features 
5. Integrating ChromaDB with llama_index's VectorStoreIndex 
6. Integrate Gemini to retrieve data 
7. Implement a frontend with Streamlit and Request library to manage API Requests  



### API End Points 
Method | Endpoints         |  Function          
-------|-------------------|------------------------------
GET    | /user             |  Get Current User 
POST   | /user             |  Create
POST   | /token            |  Login For Access Token
GET    | /user/collections |  Get Collection
POST   | /user/collections |  Add Collection
POST   | /user/query       |  Question And Answer
POST   | /user/disable     |  Logout
-------|-------------------|----------------------------



### Flow Char Diagram 
![flow_chart](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/87f23a83-8b41-45bc-b3a3-7651af98268b)



### Module Information 
- [constants.py]()
    - Contains all Global Constant elements 
    - Any modification can be done by changing this file attribute 
- [document_processor.py]()
    - contains a function that processes documents to convert small chunks of Node by applying a few metadata extractors.
    - contains a function that works on metadata and extracts required metadata 
- [drive_utils.py]()
    - contains the function that watches a drive in certain time intervals and using callbacks automatically processes and indexes the documents. 
- [vector_store.py]()
    - Contains a class ChromaVectorStoreIndex that helps to index documents using ChromaDB 
- [auth_utils]()
    - Goolge Service Build and Credential management 
    - Fast API Auth Utilities 
-[callbacks]()
    - Contains two function one is for Processing and storing data in Vector Database 
    - Second one is responsible to ask question using Gemini LLM  
- [db.setup]()
    - Creating Database setup
- [db.models]()
    - Creating Database ORM Models 
- [fast_api_main.py]()
    - This is Fast API main module 
        1. All fast API end points are define here. 
        2. In FastAPI Background Thread My Google Drive Watch Function is running while user is enable 
        3. For every user only one background task is running and Different Collections/folders are checking Linearly if updates occurs or not. 

### Front End 
- [request_manager.py] - This file contains All API Request Function for client implemented by requests module in python 
- [main.py] - main streamlit Page 
- pages  folder contains login and signup page of streamlit 







## How to **RUN**
### Step 1 : Active Google Drive API and Setup Google Credentials 
1. Goto to the [Google Cloud console](https://console.cloud.google.com/welcome/new?pli=1)
![image](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/e59f1f71-9f18-41fa-bbd3-0082908e2f03)
2. Select or Create a project   
![image-1](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/b306a9b4-d2b7-462a-8d4e-00f5cfa7c978)
3. Navigate to API and Services and click on Enable API and services 
![image-2](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/a326627f-503a-40c3-9958-00df56441745)
4. Search for Google Drive and enable `Google Drive API` and 'Google Drive Activity API' and enable both 
![image-3](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/7d51fc5b-6b43-4c3c-a83c-20bf5e707cc3)
5. Now Go back to API and Services pages as shown in 3 and Navigate to the **Credentials**
![image-4](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/ff31ceba-eddd-4f07-9a2e-8c6e881fe620)

6. Create an API Key, OAuth Client , and Service Account. Download the OAuth Client 'Client_Secret.json'
![image-5](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/e8bed4fc-be7f-455f-a59c-8757fb4ff25b)

7. Go to Service Account and create key and Download the key 
![image-6](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/2c5f0fa3-43de-4cd6-a396-df853c1ee885)

8. Place the key content and Client Secret on the example Google_Credentials folder 
### Step 2: Set API Key in .env file 
- follow this site to create easy API key https://aistudio.google.com/app/apikey

    - Please Modify the Constant Module for any changes before RUN
    - Add Google Drive OAuth Client ans Service Account Key as shown in example 
    - Create .env file as Shown in example 
#### Install Requirements
```bash
python -m venv .env 
## Run from the Git Bash Shell 
source ./env/Scripts/activate 
## Run from the Command Prompt Shell 
# ./env/Scripts/activate.bat
pip install -r requirements.txt

```
#### Running Backend Server 
With Running Backend Server Frontend Server will run automatically 
```bash
cd WebService
python fast_api_main.py
```



## Limitations 
- Llama Index's GoogleDriveReader is not able to read All types of PDF files 



## Final Output Shot 
File name : Chintan Shah- Profile Gain.pdf
Output Screen shot :
![Working Demo](https://github.com/arque1393/Document_RAG_from_GDrive_with_Llama_Index/assets/79799118/8cf752df-3b5d-4710-b2d7-34331849d6ba)

