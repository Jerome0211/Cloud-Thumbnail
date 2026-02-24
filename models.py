from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class PresetSize(str, Enum):
    small = "small"   # 150x150
    medium = "medium" # 300x300
    large = "large"   # 600x600

    def get_dimensions(self) -> tuple[int, int]:
        mapping = {
            "small": (150, 150),
            "medium": (300, 300),
            "large": (600, 600)
        }
        return mapping[self.value]

class ThumbnailMetadata(BaseModel):
    id: str = Field(..., description="Unique identifier for the thumbnail")
    original_filename: str = Field(..., description="Original name of the uploaded file")
    width: int = Field(..., description="Actual width of the generated thumbnail")
    height: int = Field(..., description="Actual height of the generated thumbnail")
    format: str = Field(..., description="Image format (e.g., JPEG, PNG)")
    url: str = Field(..., description="URL to retrieve the thumbnail image")