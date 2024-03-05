from sqlalchemy import (Column, ForeignKey, Integer, String, Boolean)
from sqlalchemy.orm import relationship
from datetime import datetime
from .setup import Base



'''This module contains All the SQLAlchemy Database Schemas or Model
'''




class User(Base): 
    __tablename__ = "user"
    user_id = Column(Integer, primary_key= True)
    username =  Column(String(100),unique=True,nullable=False)
    email = Column(String(100),unique=True, index= True, nullable= False )
    full_name = Column(String(100), nullable=False)
    _password_hash = Column(String(200), nullable=False)
    disabled = Column(Boolean, default=False)
    collection = relationship('Collection', back_populates='user')

class Collection(Base):
    __tablename__ = "collection"
    collection_id = Column(String(100), primary_key= True)
    user_id =  Column(Integer, ForeignKey('user.user_id'), nullable=False)
    user = relationship('User', back_populates='collection')