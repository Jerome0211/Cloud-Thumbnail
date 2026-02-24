import os
import uuid
from io import BytesIO
from PIL import Image, UnidentifiedImageError
from fastapi import UploadFile, HTTPException
from models import ThumbnailMetadata

STORAGE_DIR = "static/images"
os.makedirs(STORAGE_DIR, exist_ok=True)

metadata_db: dict[str, ThumbnailMetadata] = {}

def process_and_save_image(
    file: UploadFile, 
    target_width: int, 
    target_height: int, 
    base_url: str
) -> ThumbnailMetadata:

    try:
        contents = file.file.read()
        image = Image.open(BytesIO(contents))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')

        image.thumbnail((target_width, target_height))
        
        thumb_id = str(uuid.uuid4())
        filename = f"{thumb_id}.jpg"
        filepath = os.path.join(STORAGE_DIR, filename)
        
        image.save(filepath, format="JPEG", quality=85)
        
        metadata = ThumbnailMetadata(
            id=thumb_id,
            original_filename=file.filename or "unknown",
            width=image.width,
            height=image.height,
            format="JPEG",
            url=f"{base_url}/thumbnails/{thumb_id}/image"
        )
        
        metadata_db[thumb_id] = metadata
        return metadata

    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail=f"File {file.filename} is not a valid image.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing {file.filename}: {str(e)}")
    finally:
        file.file.close()

def get_metadata(thumb_id: str) -> ThumbnailMetadata:
    if thumb_id not in metadata_db:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return metadata_db[thumb_id]

def get_image_path(thumb_id: str) -> str:
    if thumb_id not in metadata_db:
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    filepath = os.path.join(STORAGE_DIR, f"{thumb_id}.jpg")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image file missing on disk")
    return filepath
