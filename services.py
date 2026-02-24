import os
import uuid
import boto3
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from database import DBThumbnail

# DigitalOcean Spaces configuration from environment variables
SPACES_KEY = os.getenv("SPACES_KEY")
SPACES_SECRET = os.getenv("SPACES_SECRET")
SPACES_REGION = os.getenv("SPACES_REGION")
SPACES_BUCKET = os.getenv("SPACES_BUCKET")

# Initialize S3 client for DigitalOcean Spaces
session = boto3.session.Session()
s3_client = session.client('s3',
    region_name=SPACES_REGION,
    endpoint_url=f"https://{SPACES_REGION}.digitaloceanspaces.com",
    aws_access_key_id=SPACES_KEY,
    aws_secret_access_key=SPACES_SECRET
)

def process_and_upload(file: UploadFile, width: int, height: int, owner_id: str, db: Session):
    """
    Processes image resizing (handling RGBA) and uploads to DO Spaces.
    Saves metadata to the database.
    """
    try:
        # 1. Read and Open Image
        contents = file.file.read()
        image = Image.open(BytesIO(contents))
        
        # 2. Fix: Handle RGBA/Transparency (Fixes "cannot write mode RGBA as JPEG")
        if image.mode in ("RGBA", "P"):
            # Create a white background for transparent images
            background = Image.new("RGB", image.size, (255, 255, 255))
            # If RGBA, use the alpha channel as a mask
            mask = image.split()[3] if image.mode == "RGBA" else None
            background.paste(image, mask=mask)
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

        # 3. Resize with Aspect Ratio
        image.thumbnail((width, height))
        
        # 4. Save to Memory Buffer
        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        # 5. Upload to DigitalOcean Spaces
        file_id = str(uuid.uuid4())
        cloud_filename = f"thumbnails/{owner_id}/{file_id}.jpg"
        
        s3_client.upload_fileobj(
            buffer,
            SPACES_BUCKET,
            cloud_filename,
            ExtraArgs={
                'ACL': 'public-read', 
                'ContentType': 'image/jpeg'
            }
        )
        
        # 6. Construct Public URL
        cloud_url = f"https://{SPACES_BUCKET}.{SPACES_REGION}.digitaloceanspaces.com/{cloud_filename}"
        
        # 7. Save Metadata to PostgreSQL
        db_record = DBThumbnail(
            id=file_id,
            owner_id=owner_id,
            original_filename=file.filename or "image.jpg",
            width=image.width,
            height=image.height,
            url=cloud_url
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        return db_record

    except Exception as e:
        print(f"Error in process_and_upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service Error: {str(e)}")
    finally:
        file.file.close()
