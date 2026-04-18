import cloudinary
import cloudinary.uploader
from app.config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET
from fastapi import UploadFile

# Configure Cloudinary once at import time
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True  # Always use HTTPS
)

async def upload_file(file: UploadFile, folder: str, public_id: str) -> str:
    """
    Uploads a file to Cloudinary and returns its permanent URL.

    Args:
        file:      The uploaded file from FastAPI
        folder:    Cloudinary folder e.g. "avatars" or "complaints"
        public_id: Unique name for the file e.g. "john_avatar"

    Returns:
        str: The permanent HTTPS URL of the uploaded file
    """
    contents = await file.read()

    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        public_id=public_id,
        overwrite=True,
        resource_type="auto"  # handles images, PDFs, docs automatically
    )

    return result["secure_url"]