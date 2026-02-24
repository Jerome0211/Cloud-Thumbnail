from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse
from typing import List, Optional
from models import PresetSize, ThumbnailMetadata
import services

router = APIRouter(prefix="/thumbnails", tags=["Thumbnails"])

@router.post("/", response_model=List[ThumbnailMetadata], status_code=201)
async def create_thumbnails(
    request: Request,
    files: List[UploadFile] = File(..., description="One or more images to upload"),
    preset: Optional[PresetSize] = Form(None, description="Preset size (small, medium, large)"),
    width: Optional[int] = Form(None, description="Custom width (must provide height if used)"),
    height: Optional[int] = Form(None, description="Custom height (must provide width if used)")
):

    if preset:
        target_width, target_height = preset.get_dimensions()
    elif width and height:
        if width <= 0 or height <= 0:
            raise HTTPException(status_code=400, detail="Width and height must be positive integers.")
        target_width, target_height = width, height
    else:
        raise HTTPException(status_code=400, detail="Must provide either 'preset' OR both 'width' and 'height'.")

    base_url = str(request.base_url).rstrip("/")
    
    results = []
    for file in files:
        metadata = services.process_and_save_image(file, target_width, target_height, base_url)
        results.append(metadata)
        
    return results

@router.get("/{thumb_id}", response_model=ThumbnailMetadata)
async def get_thumbnail_metadata(thumb_id: str):
    return services.get_metadata(thumb_id)

@router.get("/{thumb_id}/image")
async def get_thumbnail_image(thumb_id: str):
    filepath = services.get_image_path(thumb_id)
    return FileResponse(filepath, media_type="image/jpeg")
