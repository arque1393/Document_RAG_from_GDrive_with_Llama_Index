from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean, DateTime)
from sqlalchemy.orm import relationship
from datetime import datetime
from .setup import Base

from sqlalchemy.sql import func

'''This module contains All the SQLAlchemy Database Schemas or Model
'''

class User(Base): 
    __tablename__ = "user"
    user_id = Column(Integer, primary_key= True,autoincrement=True)
    username =  Column(String(100),unique=True,nullable=False)
    email = Column(String(100),unique=True, index= True, nullable= False )
    _password_hash = Column(String(200), nullable=False)
    disabled = Column(Boolean, default=True)
    one_drive_disabled = Column(Boolean, default=True)
    logout_time = Column(DateTime, default=func.now(),nullable=False)
    collection = relationship('Collection', back_populates='user')
    

class Collection(Base):
    __tablename__ = "collection"
    
    collection_id = Column(String(100), primary_key= True)
    collection_name = Column(String(100), nullable= False)
    user_id =  Column(Integer, ForeignKey('user.user_id'), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())
    one_drive_updated_at = Column(DateTime, default=func.now())
    user = relationship('User', back_populates='collection')