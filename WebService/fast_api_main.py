from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from constants import (JWT_AUTH_SECRET_KEY , ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
from datetime import  timedelta,datetime
from typing import Annotated
from models import User,UserCreate,Token,Collection,DriveFolderInfo
from db import models 
from auth_utils import (is_email_or_username_taken,get_password_hash,
                        authenticate_user,create_access_token,
                        get_current_active_user, google_auth)

from db.setup import get_session,engine
from sqlalchemy.orm import Session
from drive_utils import drive_link_to_folder_name,  read_drive_folder
from callbacks import store_data_callback
models.Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/user")
async def create(user:UserCreate, session:Session = Depends(get_session)):    
    if validate_entity := is_email_or_username_taken(user.email,user.username, models.User,session):
        raise HTTPException(status_code=400, detail=f'{validate_entity} is already taken')    
    new_user = models.User(email = user.email,username=user.username,
                        _password_hash = get_password_hash(user.password) )  
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@app.post("/token")
# @app.post("/user/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],session: Session = Depends(get_session)
) -> Token:
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
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.post("/user/collections")
async def add_collection(current_user: Annotated[User, Depends(get_current_active_user)],
                        folder_info:DriveFolderInfo, session: Session = Depends(get_session)):
    try : 
        service  = google_auth(current_user.username)
    except :
        raise HTTPException(status_code=400, detail = "Service can not be build")
    print(folder_info.folder_link)
    collection = session.query(models.Collection).filter(
                models.Collection.collection_name ==  drive_link_to_folder_name(current_user.username,folder_info.folder_link) 
                and models.Collection.user_id == current_user.user_id  
            ).first() 
    if collection :
        current_time = datetime.now()        
        try:
            read_drive_folder(service, collection.collection_name,store_data_callback, collection.updated_at  )
        except Exception as e : 
            raise HTTPException(status_code=400, detail=f'error :: {e}')
        
        collection.updated_at= current_time
        session.commit()
        session.refresh(collection)
        return {"message": "Collection Update successfully "}
    
    new_collection = models.Collection( 
                collection_name =  drive_link_to_folder_name(current_user.username,folder_info.folder_link), 
                user_id = current_user.user_id, created_at = datetime.now(), 
                updated_at =  datetime.now() )  
    
    session.add(new_collection)
    session.commit()
    session.refresh(new_collection)
    # collection_name = folder_id_to_name(drive_link_to_folder_name(folder_info.folder_link))
    try: 
        read_drive_folder(service, new_collection.collection_name,store_data_callback)
    except Exception as e : 
        raise HTTPException(status_code=500,detail=f'error :: {e}')
    
    return {"message": "Collection Add successfully "}

@app.get("/user/collections")
async def get_collection(current_user: Annotated[User, Depends(get_current_active_user)], session: Session= Depends(get_session)):
    return session.query(models.Collection).filter_by(user_id = current_user.user_id).all() 
