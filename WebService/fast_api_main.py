import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from db import models 
from constants import  ACCESS_TOKEN_EXPIRE_MINUTES, MS_CLIENT_ID
from datetime import  timedelta,datetime
from models import User,UserCreate,Token,DriveFolderInfo,Query
from auth_utils import (get_current_active_user,authenticate_user,google_auth,
            is_email_or_username_taken,get_password_hash,create_access_token, MSAuth)

from drive_utils import( drive_link_to_folder_name_and_id,read_drive_folder,
            watch_drive_load_data,DriveFolderDoesNotExist,check_folder_permission)
from db.setup import get_session,engine
from sqlalchemy.orm import Session
from callbacks import store_data_callback, get_answer, store_data_from_onedrive
from contextlib import asynccontextmanager

### Connecting Frontend 
from fastapi.responses import RedirectResponse
from subprocess import Popen, DEVNULL
Popen(["streamlit", "run", "../Frontend/main.py"], stdout=DEVNULL, stderr=DEVNULL)









models.Base.metadata.create_all(engine)
app = FastAPI()

# @app.on_event("shutdown")
# async def shutdown_event( session:Session = Depends(get_session)):
#     for user in session.query(models.User).all() :
#         user.disabled = True 
#         session.commit()
#         session.refresh(user)


@app.get('/')
async def frontend():
    return RedirectResponse(url="http://localhost:8501")

@app.post("/user")
async def create(user:UserCreate, background_task : BackgroundTasks, session:Session = Depends(get_session)):    
    if validate_entity := is_email_or_username_taken(user.email,user.username, models.User,session):
        raise HTTPException(status_code=400, detail=f'{validate_entity} is already taken')    
    new_user = models.User(email = user.email,username=user.username,disabled = True,
                        _password_hash = get_password_hash(user.password) )  

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    

    # try : 
    #     drive_service,drive_activity_service  = google_auth(user.username)
    #     background_task.add_task( watch_drive_load_data , drive_activity_service, session,new_user.user_id, store_data_callback(new_user.username)) 
    # except Exception as e:
    #     new_user.disabled=True  
    #     raise HTTPException(status_code=400, detail = f"Service can not be build")
    # finally:
    #     session.commit()
    #     session.refresh(new_user)
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/token" )
# @app.post("/user/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session) ) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # if user.disabled :
    #     user.disabled= False
    #     session.commit()
    #     session.refresh(user)
        # try : 
        #     drive_service,drive_activity_service  = google_auth(form_data.username)
        # except :
        #     raise HTTPException(status_code=400, detail = "Service can not be build")
        # background_task.add_task( watch_drive_load_data , drive_activity_service, session,user.user_id, store_data_callback(user.username))
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )    
    return Token(access_token=access_token, token_type="bearer")
    
@app.get("/user", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

# @app.post("/user/collections")
# async def add_collection(current_user: Annotated[User, Depends(get_current_active_user)],
#                         folder_info:DriveFolderInfo, session: Session = Depends(get_session)):
#     try : 
#         drive_service,drive_activity_service  = google_auth(current_user.username)
#     except :
#         raise HTTPException(status_code=400, detail = "Service can not be build")
#     try:
#         folder_name, folder_id =  drive_link_to_folder_name_and_id(drive_service,folder_info.folder_link)
#     except: 
#         raise HTTPException(status_code=400, detail = "Provided Link Can not a proper Google Drive Link")
#     collection = session.query(models.Collection).filter(
#                 models.Collection.collection_id == folder_id
#                 and models.Collection.user_id == current_user.user_id  
#             ).first() 
#     if collection :        
#         collection.updated_at =  datetime.now() 
#         session.commit()
#         session.refresh(collection)
#         raise HTTPException(status_code=400, detail=' "Collection is Already Exist "')  

    # try:
    #     if check_folder_permission(drive_service,folder_id) == 'anyone':
    #         read_drive_folder(drive_activity_service, folder_id ,folder_name, store_data_callback(current_user.username))
    #     else: 
    #         raise HTTPException(status_code= 403, detail = "Folder is restricted Please give the view permission for everyone")
    # except DriveFolderDoesNotExist as e :
    #     raise HTTPException(status_code=404,detail=f'{e}')
    # except Exception as e : 
    #     raise HTTPException(status_code=500,detail=f'error :: {e}')
    # new_collection = models.Collection( 
    #         collection_id = folder_id,
    #         collection_name =  folder_name,
    #         user_id = current_user.user_id, created_at = datetime.now(), 
    #         updated_at =  datetime.now() )  
    
    # session.add(new_collection)
    # session.commit()
    # session.refresh(new_collection)
    # return {"message": "Collection Add successfully "}

@app.post('/user/connect/google_drive')
async def connect_google_drive (current_user: Annotated[User, Depends(get_current_active_user)],
                                background_task:BackgroundTasks,session: Session = Depends(get_session)):
    response:dict ={'message': ""}
    
    try : 
        drive_service,drive_activity_service  = google_auth(current_user.username)
    except Exception as e:        
        raise HTTPException(status_code=400, detail = f"Service can not be build  : {e}")
    
    
    
    if not session.query(models.Collection).filter_by(user_id=current_user.user_id).first():  
        if not read_drive_folder(drive_service,current_user.username, callbacks=store_data_callback(current_user.username)):
            response["message"]+= "Connected to Drive, "
        else :
            response["message"]+= "Connected to Drive, No new data found, "
        new_collection =  models.Collection(collection_id=current_user.username,
                                        collection_name=current_user.username, user_id=current_user.user_id,
                                        created_at = datetime.now(), updated_at =  datetime.now()) 
        session.add(new_collection)
        session.commit()
        session.refresh(new_collection)
    if current_user.disabled :    
        try:
            background_task.add_task( watch_drive_load_data , drive_activity_service,
                                session,current_user.user_id, store_data_callback(current_user.username)) 
            current_user.disabled=False  
            response['message'] += " Background Pipeline is running"
        except:
            current_user.disabled=True  
            raise HTTPException(status_code=400, detail = f"Background task can not started")
        finally:
            session.commit()
            session.refresh(current_user)
        
    return response

### ONE DRIVE ENDPOINTS ####
@app.post('/user/connect/one_drive')
async def connect_one_drive (current_user: Annotated[User, Depends(get_current_active_user)]): 
    msauth = MSAuth(client_id=MS_CLIENT_ID)
    if user_code := msauth.get_token(current_user.username):
        return {"user_code":user_code, 'message':"Enter the code and login" }
    try: 
        _ = msauth._access_token
        return {'message':"Connected" }
    except Exception as e : 
        raise HTTPException(status_code=401, detail= f'{e}')
    

@app.post('/user/connect/one_drive/verify')
async def connect_one_drive (current_user: Annotated[User, Depends(get_current_active_user)]):  
    try :
        msauth = MSAuth(client_id=MS_CLIENT_ID)  
        _ = msauth.get_token(current_user.username)      
        _ = msauth._access_token  
        return {'message':"Connected" }
    except Exception as e : 
        raise HTTPException(status_code=401, detail= f'{e}')




@app.post('/user/connect/one_drive/read')
async def connect_one_drive (current_user: Annotated[User, Depends(get_current_active_user)],session: Session = Depends(get_session)):  
    response= {"message":""}
    if not session.query(models.Collection).filter_by(user_id=current_user.user_id).first():
        new_collection =  models.Collection(collection_id=current_user.username,
                        collection_name=current_user.username, user_id=current_user.user_id,
                        created_at = datetime.now(), updated_at =  datetime.now())     
        session.add(new_collection)
        session.commit()
        session.refresh(new_collection)
    msauth = MSAuth(client_id=MS_CLIENT_ID)  
    _ = msauth.get_token(current_user.username)      
    access_token = msauth._access_token  
    store_data_from_onedrive(username=current_user.username, access_token=access_token)
    



@app.get("/user/collections")
async def get_collection(current_user: Annotated[User, Depends(get_current_active_user)], session: Session= Depends(get_session)):
    return session.query(models.Collection).filter_by(user_id = current_user.user_id).all() 



@app.post("/user/query")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], query:Query ):
    answer,metadata = get_answer(current_user.username, current_user.username, query.question)
    return {'answer':answer, 'metadata':metadata} 

@app.post("/user/disable")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], session:Session=Depends(get_session) ):
    current_user.disabled = True 
    session.commit()
    session.refresh(current_user)
    return {"message":"Logout Success"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)