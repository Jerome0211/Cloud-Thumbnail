from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from database import SessionLocal, DBUser, DBThumbnail
import services

router = APIRouter(tags=["Thumbnails"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(token: str = Depends(oauth2_scheme)):
    return token 

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.username == form_data.username).first()
    if not user:
        user = DBUser(username=form_data.username, hashed_password=form_data.password)
        db.add(user)
        db.commit()
    return {"access_token": user.username, "token_type": "bearer"}

@router.post("/thumbnails/")
async def create_thumbnail(
    files: List[UploadFile] = File(...),
    width: int = Form(300),
    height: int = Form(300),
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = []
    for file in files:
        res = services.process_and_upload(file, width, height, current_user, db)
        results.append(res)
    return results

@router.get("/thumbnails/me")
async def get_my_thumbnails(current_user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(DBThumbnail).filter(DBThumbnail.owner_id == current_user).all()