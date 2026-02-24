import os
import uuid
import boto3
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import DBThumbnail

# DigitalOcean Spaces Config
SPACES_KEY = os.getenv("SPACES_KEY")
SPACES_SECRET = os.getenv("SPACES_SECRET")
SPACES_REGION = os.getenv("SPACES_REGION")
SPACES_BUCKET = os.getenv("SPACES_BUCKET")

session = boto3.session.Session()
s3_client = session.client('s3',
    region_name=SPACES_REGION,
    endpoint_url=f"https://{SPACES_REGION}.digitaloceanspaces.com",
    aws_access_key_id=SPACES_KEY,
    aws_secret_access_key=SPACES_SECRET
)

def process_and_upload(file: UploadFile, width: int, height: int, owner_id: str, db: Session):
    try:
        contents = file.file.read()
        img = Image.open(BytesIO(contents))
        
        # Resize
        img.thumbnail((width, height))
        
        # Save to buffer
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        # Upload
        file_id = str(uuid.uuid4())
        cloud_filename = f"thumbnails/{owner_id}/{file_id}.jpg"
        
        s3_client.upload_fileobj(
            buffer,
            SPACES_BUCKET,
            cloud_filename,
            ExtraArgs={'ACL': 'public-read', 'ContentType': 'image/jpeg'}
        )
        
        cloud_url = f"https://{SPACES_BUCKET}.{SPACES_REGION}.digitaloceanspaces.com/{cloud_filename}"
        
        # DB Record
        db_record = DBThumbnail(
            id=file_id,
            owner_id=owner_id,
            original_filename=file.filename,
            width=img.width,
            height=img.height,
            url=cloud_url
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

