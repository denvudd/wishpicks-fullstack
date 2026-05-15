from pydantic import BaseModel, ConfigDict


class MediaUploadData(BaseModel):
    url: str


class MediaUploadResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"data": {"url": "https://res.cloudinary.com/wishpicks/image/upload/avatars/abc123.jpg"}}
        }
    )

    data: MediaUploadData
