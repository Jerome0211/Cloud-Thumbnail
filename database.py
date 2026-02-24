import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String) 

class DBThumbnail(Base):
    __tablename__ = "thumbnails"
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.username"))
    original_filename = Column(String)
    url = Column(String) 
    width = Column(Integer)
    height = Column(Integer)

Base.metadata.create_all(bind=engine)