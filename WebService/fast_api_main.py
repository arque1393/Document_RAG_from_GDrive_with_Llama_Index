import uvicorn 
from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from db import models 
import time 
from constants import  ACCESS_TOKEN_EXPIRE_MINUTES, MS_CLIENT_ID, ONEDRIVE_CREDENTIAL_DIR,ONEDRIVE_LOGIN_EXPIRE_DURATION
from datetime import  timedelta,datetime
from models import User,UserCreate,Token,DriveFolderInfo,Query
from auth_utils import (get_current_active_user,authenticate_user,google_auth,
            is_email_or_username_taken,get_password_hash,create_access_token, MSAuth)

from drive_utils import( read_drive_folder,watch_one_drive_load_data,
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
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )    
    return Token(access_token=access_token, token_type="bearer")
    
@app.get("/user", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user

@app.post('/user/connect/google_drive')
async def connect_google_drive (current_user: Annotated[User, Depends(get_current_active_user)],
                                background_task:BackgroundTasks,session: Session = Depends(get_session)):
    response:dict ={'message': "Already Connected"}
    
    try : 
        drive_service,drive_activity_service  = google_auth(current_user.username)
    except Exception as e:        
        raise HTTPException(status_code=400, detail = f"Service can not be build  : {e}")
    
    
    
    if not session.query(models.Collection).filter_by(user_id=current_user.user_id).first():  
        if read_drive_folder(drive_service,current_user.username, callbacks=store_data_callback(current_user.username)):
            response["message"] = "Connected to Drive, Drive has been read "
        else :
            response["message"] = "Connected to Drive, No new data found, "
        new_collection =  models.Collection(collection_id=current_user.username,
                                        collection_name=current_user.username, user_id=current_user.user_id,
                                        created_at = datetime.now(), updated_at =  datetime.now(), one_drive_updated_at = datetime.now()) 

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
async def connect_one_drive (current_user: Annotated[User, Depends(get_current_active_user)],
                            background_task:BackgroundTasks, session : Session= Depends(get_session)):  
    try :
        msauth = MSAuth(client_id=MS_CLIENT_ID)  
        _ = msauth.get_token(current_user.username)      
        _ = msauth._access_token  
        response =  {'message':"Connected" }
    except Exception as e: 
        raise HTTPException(status_code=401, detail= f'{e}')

    if not session.query(models.Collection).filter_by(user_id=current_user.user_id).first():  
        store_data_from_onedrive(username=current_user.username, access_token = msauth._access_token)
        new_collection =  models.Collection(collection_id=current_user.username,
                                        collection_name=current_user.username, user_id=current_user.user_id,
                                        created_at = datetime.now(), updated_at =  datetime.now(), one_drive_updated_at = datetime.now()) 
        session.add(new_collection)
        session.commit()
        session.refresh(new_collection)
        response['message']+= "Reading One Drive Successful "
    if current_user.one_drive_disabled :
        background_task.add_task(watch_one_drive_load_data, session, current_user.username, current_user.user_id, store_data_from_onedrive)  
        response['message']+= "Background Onedrive Automation is running "
        current_user.one_drive_disabled = False 
        session.add(current_user)
        session.commit()
        session.refresh(current_user)
    return response 
    
    # except Exception as e : 
    #     raise HTTPException(status_code=401, detail= f'{e}')




@app.post('/user/connect/one_drive/read')
async def read_data_from_one_drive(current_user: Annotated[User, Depends(get_current_active_user)],session: Session = Depends(get_session)):  
    response = {"message":""}
    if not session.query(models.Collection).filter_by(user_id=current_user.user_id).first():
        new_collection =  models.Collection(collection_id=current_user.username,
                        collection_name=current_user.username, user_id=current_user.user_id,
                        created_at = datetime.now(), updated_at =  datetime.now())     
        session.add(new_collection)
        session.commit()
        session.refresh(new_collection)
    c_time = time.time()
    while not (ONEDRIVE_CREDENTIAL_DIR/current_user.username/'token.b').exist() :
        if time.time()- c_time > ONEDRIVE_LOGIN_EXPIRE_DURATION : 
            raise HTTPException(status_code=401, detail='Microsoft Auth Token is not found')
        # time.sleep (.1)
        continue
    msauth = MSAuth(client_id=MS_CLIENT_ID)  
    _ = msauth.get_token(current_user.username)      
    try : access_token = msauth._access_token  
    except : raise HTTPException(status_code=401, detail = 'Not Connected to microsoft')
    try:
        store_data_from_onedrive(username=current_user.username, access_token=access_token)
        response['message']='Data has been read'
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'{e}')
    return response



@app.get("/user/collections")
async def get_collection(current_user: Annotated[User, Depends(get_current_active_user)], session: Session= Depends(get_session)):
    return session.query(models.Collection).filter_by(user_id = current_user.user_id).all() 



@app.post("/user/query")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], query:Query ):
    answer,metadata = get_answer(current_user.username, current_user.username, query.question)
    return {'answer':answer, 'metadata':metadata} 

@app.post("/user/disable")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], session:Session=Depends(get_session) ):
    # current_user.disabled = True 
    # current_user.one_drive_disabled = True 
    current_user.logout_time = datetime.now()
    session.commit()
    session.refresh(current_user)
    return {"message":"Logout Success"}

if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)