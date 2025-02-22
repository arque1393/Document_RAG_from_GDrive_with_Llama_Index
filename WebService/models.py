
from pydantic import BaseModel, EmailStr,Field
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    user_id:int
    username: str
    email: str
    disabled: bool
    one_drive_disabled:bool
    _password_hash:str
    class Config:
        orm_mode = True

class UserInDB(User):
    _password_hash:str


class UserCreate(BaseModel):
    username:str = Field(..., min_length=6,max_length=100)
    email: EmailStr 
    password:str = Field(..., min_length=4,max_length=100)

class Collection(BaseModel):
    collection_id:str
    user_id:int
    
class DriveFolderInfo(BaseModel):
    folder_link : str
    
    
class Query (BaseModel):
    # collection_name:str
    question:str