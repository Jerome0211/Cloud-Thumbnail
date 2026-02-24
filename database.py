import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker

# Get DATABASE_URL from environment variables
db_url = os.getenv("DATABASE_URL")

# 1. Fix: SQLAlchemy 1.4+ requires 'postgresql://' instead of 'postgres://'
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Fallback to local SQLite if no DATABASE_URL is provided (useful for local testing)
if not db_url:
    db_url = "sqlite:///./app.db"

# 2. Fix: Add SSL requirements for Managed Cloud Databases
# SQLite does not support connect_args, so we handle it conditionally
if "sqlite" in db_url:
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
else:
    # sslmode=require is essential for DigitalOcean Managed Databases
    engine = create_engine(db_url)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Table Model
class DBUser(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String) 

# Thumbnail Metadata Table Model
class DBThumbnail(Base):
    __tablename__ = "thumbnails"
    id = Column(String, primary_key=True, index=True)
    owner_id = Column(String, ForeignKey("users.username"))
    original_filename = Column(String)
    url = Column(String) 
    width = Column(Integer)
    height = Column(Integer)

# Create all tables in the database
def init_db():
    Base.metadata.create_all(bind=engine)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Execute table creation
init_db()
