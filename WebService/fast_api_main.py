import uvicorn 


from fastapi import Depends, FastAPI, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from db import models 
from constants import  ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import  timedelta,datetime
from models import User,UserCreate,Token,DriveFolderInfo,Query
from auth_utils import (is_email_or_username_taken,get_password_hash,
                        authenticate_user,create_access_token,
                        get_current_active_user, google_auth)

from db.setup import get_session,engine
from sqlalchemy.orm import Session
from drive_utils import drive_link_to_folder_name_and_id,  read_drive_folder,watch_drive_load_data
from callbacks import store_data_callback, get_answer

models.Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/user")
async def create(user:UserCreate, background_task : BackgroundTasks, session:Session = Depends(get_session)):    
    if validate_entity := is_email_or_username_taken(user.email,user.username, models.User,session):
        raise HTTPException(status_code=400, detail=f'{validate_entity} is already taken')    
    new_user = models.User(email = user.email,username=user.username,
                        _password_hash = get_password_hash(user.password) )  
    new_user.disabled=False
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    
    #### Enable Background Task 
    try : 
        drive_service,drive_activity_service  = google_auth(user.username)
    except :
        raise HTTPException(status_code=400, detail = "Service can not be build")
    background_task.add_task( watch_drive_load_data , drive_activity_service, session,new_user.user_id, store_data_callback(new_user.username)) 
    ###
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")

@app.post("/token" )
# @app.post("/user/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    background_task : BackgroundTasks, session: Session = Depends(get_session) ) -> Token:
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.disabled :
        user.disabled= False
        session.commit()
        session.refresh(user)
 
        try : 
            drive_service,drive_activity_service  = google_auth(form_data.username)
        except :
            raise HTTPException(status_code=400, detail = "Service can not be build")
        background_task.add_task( watch_drive_load_data , drive_activity_service, session,user.user_id, store_data_callback(user.username))
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )    
    return Token(access_token=access_token, token_type="bearer")
    
@app.get("/user", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.post("/user/collections")
async def add_collection(current_user: Annotated[User, Depends(get_current_active_user)],
                        folder_info:DriveFolderInfo, session: Session = Depends(get_session)):
    try : 
        drive_service,drive_activity_service  = google_auth(current_user.username)
    except :
        raise HTTPException(status_code=400, detail = "Service can not be build")
    
    folder_name, folder_id =  drive_link_to_folder_name_and_id(drive_service,folder_info.folder_link)
    
    collection = session.query(models.Collection).filter(
                models.Collection.collection_id == folder_id
                and models.Collection.user_id == current_user.user_id  
            ).first() 
    if collection :
        
        # try:
        #     read_drive_folder(drive_activity_service, folder_id ,folder_name, store_data_callback(current_user.username), collection.updated_at  )
        # except Exception as e : 
        #     raise HTTPException(status_code=400, detail=f'error :: {e}')
        
        collection.updated_at =  datetime.now() 
        session.commit()
        session.refresh(collection)
        raise HTTPException(status_code=400, detail=' "Collection is Already Exist "')  
    

    try: 
        read_drive_folder(drive_activity_service, folder_id ,folder_name, store_data_callback(current_user.username))
    except Exception as e : 
        raise HTTPException(status_code=500,detail=f'error :: {e}')
    new_collection = models.Collection( 
            collection_id = folder_id,
            collection_name =  folder_name,
            user_id = current_user.user_id, created_at = datetime.now(), 
            updated_at =  datetime.now() )  
    
    session.add(new_collection)
    session.commit()
    session.refresh(new_collection)
    return {"message": "Collection Add successfully "}

@app.get("/user/collections")
async def get_collection(current_user: Annotated[User, Depends(get_current_active_user)], session: Session= Depends(get_session)):
    return session.query(models.Collection).filter_by(user_id = current_user.user_id).all() 



@app.post("/user/query")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], query:Query ):
    answer,metadata = get_answer(current_user.username, query.collection_name, query.question)
    return {'answer':answer, 'metadata':metadata} 

@app.post("/user/disable")
async def question_and_answer(current_user: Annotated[User, Depends(get_current_active_user)], session:Session=Depends(get_session) ):
    current_user.disabled = True 
    session.commit()
    session.refresh(current_user)
    
    
if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)