from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from constants import (JWT_AUTH_SECRET_KEY , ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)
from datetime import  timedelta
from typing import Annotated
from models import User,UserCreate,Token,Collection,DriveFolderInfo
from db import models 
from auth_utils import (is_email_or_username_taken,get_password_hash,
                        authenticate_user,create_access_token,
                        get_current_active_user)
from db.setup import get_session,engine
from sqlalchemy.orm import Session
from drive_utils import drive_link_to_id, folder_id_to_name, read_drive_folder
models.Base.metadata.create_all(engine)
app = FastAPI()

@app.post("/user")
async def create(user:UserCreate, session:Session = Depends(get_session)):    
    if validate_entity := is_email_or_username_taken(user.email,user.username, models.User,session):
        raise HTTPException(status_code=400, detail=f'{validate_entity} is already taken')    
    new_user = models.User(email = user.email,username=user.username,
                        full_name= user.full_name, 
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
    if collection := session.query(models.Collection).filter_by(collection_id =  drive_link_to_id(folder_info.folder_link)).first()
        raise HTTPException(status_code=400, detail='Collection is exist is already taken')  
    session.add(collection)
    session.commit()
    session.refresh(collection)
    collection_name = folder_id_to_name(drive_link_to_id(folder_info.folder_link))
    read_drive_folder(collection_name)
@app.get("/user/collections")
async def add_collection(current_user: Annotated[User, Depends(get_current_active_user)], query:Collection):