

## Project Information 
### **Title** : : Intelligent Document Finder with Llama Index 

### Features : 
1. Automatic Retrieve data from Google Drive folders.
    - System Check in certain time interval if changes occurs on selected Google Drive if occurs then it decode that and read newly created or updated files from the Google Drive and **store** all the data in a vector database for future search 
    - As Vector Database ```ChromaDB``` has been used 
2. Retrieve any text based document files 
    - System is able to retrieve any kind of text information files Ex. Documents, PDF, PPD, HTML, Markdown etc.
    - Using ```llama_index.readers.google.GoogleDriveReader``` to load all document from the selected Google Drive folder 
3. Preprocessing and Vector Store Indexing :
    - Index all the retrieve data by making few pre process like Title Extraction , Paragraph Extraction, etc. 
4. Integrating Google's Gemini Model as LLM to answer the Query 

### Process 
1. Create Google Drive Credential and Service Account 
2. Activate Google Drive API Service 
3. Implement Google Drive Monitoring System 
    - Requesting for activity Google Drive to fetch data during certain time intervals 
    - Checking Changes are available or not 
    - If available read files that are changed 
4. Process data to extract features 
5. Integrating ChromaDB with llama_index's VectorStoreIndex 
6. Integrate Gemini to retrieve data 
7. Implement a frontend with Gradio 

### Module Information 
- [constants.py]()
- [document_processor.py]()
- [drive_utils.py]()
- [interface.py]()
- [vector_store.py]()
- [main.py]()

### How to **RUN**

Please Modify the Constant Module for any changes before RUN
```bash
python -m venv .env 
## Run from the Git Bash Shell 
source ./env/Scripts/activate 
## Run from the Command Prompt Shell 
# ./env/Scripts/activate.bat
pip install -r requirements.txt
cd WebService
python main.py
```


