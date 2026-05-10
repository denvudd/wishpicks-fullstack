import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.models.user import User
from app.schemas.items import WishItemPositionUpdate, WishItemSingleResponse, WishItemUpdate
from app.services import items as item_service

router = APIRouter()


@router.get(
    "/{item_id}",
    summary="Get a wish item",
    response_model=WishItemSingleResponse,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Item not found"},
    },
)
async def get_item(
    item_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemSingleResponse:
    item = await item_service.get_item_by_id(db, item_id)
    is_reserved = await item_service.get_is_reserved(db, item.id)
    return WishItemSingleResponse(data=item_service.build_item_response(item, is_reserved))


@router.patch(
    "/{item_id}",
    summary="Update a wish item",
    response_model=WishItemSingleResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Item not found"},
        422: {"description": "Validation error"},
    },
)
async def update_item(
    item_id: uuid.UUID,
    body: WishItemUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemSingleResponse:
    item = await item_service.get_item_for_owner(db, item_id, current_user)
    updated = await item_service.update_item(db, item, body)
    is_reserved = await item_service.get_is_reserved(db, updated.id)
    return WishItemSingleResponse(data=item_service.build_item_response(updated, is_reserved))


@router.delete(
    "/{item_id}",
    summary="Delete a wish item",
    status_code=204,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Item not found"},
    },
)
async def delete_item(
    item_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = await item_service.get_item_for_owner(db, item_id, current_user)
    await item_service.delete_item(db, item)


@router.patch(
    "/{item_id}/position",
    summary="Update sort position of a wish item",
    response_model=WishItemSingleResponse,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Forbidden — not the owner"},
        404: {"description": "Item not found"},
        422: {"description": "Validation error"},
    },
)
async def update_position(
    item_id: uuid.UUID,
    body: WishItemPositionUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> WishItemSingleResponse:
    item = await item_service.get_item_for_owner(db, item_id, current_user)
    updated = await item_service.update_position(db, item, body.position)
    is_reserved = await item_service.get_is_reserved(db, updated.id)
    return WishItemSingleResponse(data=item_service.build_item_response(updated, is_reserved))
