from fastapi import APIRouter, Depends, File, Form, Request, UploadFile

from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.models.user import User
from app.schemas.media import MediaUploadData, MediaUploadResponse
from app.services import media as media_service

router = APIRouter()


@router.post(
    "/upload",
    response_model=MediaUploadResponse,
    summary="Upload an image to Cloudinary",
    responses={
        400: {"description": "Invalid file type, file exceeds 5 MB, or invalid folder value"},
        401: {"description": "Not authenticated"},
        422: {"description": "Cloudinary upload failed"},
    },
    tags=["media"],
)
@limiter.limit("20/minute")
async def upload_image(
    request: Request,
    file: UploadFile = File(..., description="JPEG, PNG, or WebP; max 5 MB"),
    folder: str = Form("general", description="One of: avatars, covers, items, general"),
    current_user: User = Depends(get_current_user),
) -> MediaUploadResponse:
    file_bytes = await file.read()
    url, width, height = await media_service.upload_image(file_bytes, file.content_type or "", folder)
    return MediaUploadResponse(data=MediaUploadData(url=url, width=width, height=height))
