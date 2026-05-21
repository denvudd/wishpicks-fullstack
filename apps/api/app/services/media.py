import asyncio

import cloudinary.uploader
from fastapi import HTTPException

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_ALLOWED_FOLDERS = {"avatars", "covers", "items", "general"}
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB


async def upload_image(file_bytes: bytes, content_type: str, folder: str) -> tuple[str, int, int]:
    if content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Only JPEG, PNG, and WebP images are accepted.",
                }
            },
        )

    if len(file_bytes) > _MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": "File must not exceed 5 MB.",
                }
            },
        )

    if folder not in _ALLOWED_FOLDERS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "INVALID_FOLDER",
                    "message": f"folder must be one of: {', '.join(sorted(_ALLOWED_FOLDERS))}.",
                }
            },
        )

    try:
        result = await asyncio.to_thread(
            cloudinary.uploader.upload,
            file_bytes,
            folder=f"wishpicks/{folder}",
            resource_type="image",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": {
                    "code": "UPLOAD_FAILED",
                    "message": "Failed to upload image to storage.",
                }
            },
        ) from exc

    return result["secure_url"], result["width"], result["height"]
