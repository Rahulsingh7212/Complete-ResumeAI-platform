# app/utils/cloudinary_upload.py

import io
import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.config.settings import settings

# Configure Cloudinary
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)

def upload_pdf(file_bytes: bytes, filename: str, user_id: str) -> dict:
    """
    Upload a PDF file to Cloudinary.
    Returns upload result with URL and public_id.
    """
    result = cloudinary.uploader.upload(
        io.BytesIO(file_bytes),
        resource_type="raw",             # Use "raw" for PDFs
        folder=f"{settings.CLOUDINARY_FOLDER}/{user_id}",
        public_id=f"{filename.split('.')[0]}_{user_id[:8]}",
        tags=["resume", user_id],
        use_filename=True,
        unique_filename=True,
    )

    return {
        "url": result.get("secure_url"),
        "public_id": result.get("public_id"),
        "bytes": result.get("bytes"),
        "format": result.get("format"),
        "created_at": result.get("created_at"),
    }


def delete_pdf(public_id: str) -> bool:
    """Delete a PDF from Cloudinary."""
    try:
        cloudinary.uploader.destroy(public_id, resource_type="raw")
        return True
    except Exception:
        return False