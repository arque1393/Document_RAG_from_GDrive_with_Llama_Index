
from pydantic import BaseModel, EmailStr
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
    _password_hash:str
    class Config:
        orm_mode = True

class UserInDB(User):
    _password_hash:str


class UserCreate(BaseModel):
    username: str
    email: EmailStr 
    password:str

class Collection(BaseModel):
    collection_id:str
    user_id:int
    
class DriveFolderInfo(BaseModel):
    folder_link : str
    
    
class Query (BaseModel):
    collection_name:str
    question:str