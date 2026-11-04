from PIL import Image
from io import BytesIO
from fastapi import HTTPException, UploadFile, status
import uuid
from pathlib import Path
from app.core.config import settings

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/bmp"
}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

async def validate_and_save_upload(file: UploadFile) -> str:
    """Validate uploaded image integrity, dimensions, size, and save safely."""
    # Validate mime
    if file.content_type and file.content_type.lower() not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type: {file.content_type}. Supported: JPEG, PNG, WEBP, BMP."
        )
        
    # Validate extension
    ext = ".jpg"
    if file.filename:
        suffix = Path(file.filename).suffix.lower()
        if suffix in ALLOWED_EXTENSIONS:
            ext = suffix
            
    # Read payload
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )
        
    if len(content) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image size exceeds the maximum limit of {settings.MAX_UPLOAD_SIZE_MB}MB."
        )
        
    # Verify image with Pillow
    try:
        stream = BytesIO(content)
        img = Image.open(stream)
        img.verify()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid image data."
        )
        
    # Save temporary file inside originals directory
    safe_name = f"temp_{uuid.uuid4().hex[:12]}{ext}"
    temp_path = settings.originals_dir / safe_name
    
    with open(temp_path, "wb") as f:
        f.write(content)
        
    return str(temp_path)
