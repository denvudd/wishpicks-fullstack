import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReservationCreate(BaseModel):
    reserver_name: str | None = None

    model_config = ConfigDict(json_schema_extra={"example": {"reserver_name": "Олена"}})


class ReservationResponse(BaseModel):
    id: uuid.UUID
    item_id: uuid.UUID
    reserver_name: str | None
    is_fulfilled: bool
    anon_token: str | None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440001",
                "item_id": "770e8400-e29b-41d4-a716-446655440000",
                "reserver_name": "Олена",
                "is_fulfilled": False,
                "anon_token": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2026-05-10T12:00:00Z",
            }
        },
    )


class ReservationSingleResponse(BaseModel):
    data: ReservationResponse


class FulfillRequest(BaseModel):
    is_fulfilled: bool

    model_config = ConfigDict(json_schema_extra={"example": {"is_fulfilled": True}})
