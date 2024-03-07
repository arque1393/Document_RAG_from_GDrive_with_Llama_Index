from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
'''This module contains Database Configuration Variable, Database connection String database engine and database access utility  '''

# # SQLite setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# PostgreSQL Database Configuration
# USER = 'my_user'
# DATABASE = 'my_database'
# PASSWORD = 'Password'
# HOST = 'localhost'
# PORT = 5432

# # PostgreSQL Connection
# SQLALCHEMY_DATABASE_URL = f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
# engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# BASE ORM Model 
Base = declarative_base()


# DB Utilities 
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()