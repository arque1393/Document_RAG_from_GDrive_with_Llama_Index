
from pydantic import BaseModel 

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str
    full_name: str
    disabled: bool
    _password_hash:str
    class Config:
        orm_mode = True

class UserInDB(User):
    _password_hash:str


class UserCreate(BaseModel):
    username: str
    email: str 
    full_name: str 
    disabled: bool 
    password:str

class Collection(BaseModel):
    collection_id:str
    user_id:int