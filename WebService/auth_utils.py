from datetime import datetime, timedelta, timezone
from models import TokenData,User,UserInDB
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Annotated
from fastapi import Depends, HTTPException, status
from constants import  JWT_AUTH_SECRET_KEY , ALGORITHM
from db.setup import get_session, Base
from pydantic import EmailStr
from db import models 
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")




def is_email_or_username_taken(email: EmailStr,username:str, model:Base , session:Session ) -> bool | str:
    '''check in database the given email is already exist or not
input:
    email : Email String
    model : model or table where to check
    session : SQLAlchemy Database Session Utility 
return str: 
    return 'email' if email exist 
    return 'username' if username exist 
    return None for new user 
'''
    existing_object = session.query(model).filter_by(email=email).first()
    if existing_object  : 
        return 'email' 
    existing_object = session.query(model).filter_by(username=username).first()
    if existing_object:
        return 'username'
    
    return False
    
## Helper Functions 
def verify_password(plain_password, hashed_password):
    """Password Verification by converting Hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Return Hash of any string """
    return pwd_context.hash(password)



    

def authenticate_user(username: str, password: str, session:Session):
    if user := session.query(models.User).filter_by(username=username).first():
        print ( user)
        return user if verify_password(password, user._password_hash) else False
    else: return False


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode["exp"] = expire
    return  jwt.encode(to_encode, JWT_AUTH_SECRET_KEY, algorithm=ALGORITHM)



async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],session:Session=Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_AUTH_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    if user := session.query(models.User).filter_by(username=username).first():
        return user
    raise credentials_exception
    


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

