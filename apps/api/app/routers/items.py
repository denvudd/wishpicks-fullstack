import uuid

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.limiter import limiter
from app.dependencies.get_current_user import get_current_user
from app.dependencies.get_db import get_db
from app.dependencies.get_redis import get_redis
from app.models.user import User
from app.schemas.items import (
    ParseUrlData,
    ParseUrlRequest,
    ParseUrlResponse,
    WishItemPositionUpdate,
    WishItemSingleResponse,
    WishItemUpdate,
)
from app.services import items as item_service
from app.services import url_parser as url_parser_service

router = APIRouter()


@router.post(
    "/parse-url",
    summary="Parse a product URL and extract wish item fields",
    response_model=ParseUrlResponse,
    responses={
        400: {"description": "Invalid URL scheme"},
        401: {"description": "Not authenticated"},
        422: {"description": "Failed to fetch or parse the URL"},
    },
)
@limiter.limit("10/minute")
async def parse_product_url(
    body: ParseUrlRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    redis=Depends(get_redis),
) -> ParseUrlResponse:
    result = await url_parser_service.parse_url(body.url, redis)
    return ParseUrlResponse(
        data=ParseUrlData(
            title=result.title,
            description=result.description,
            image_url=result.image_url,
            price=result.price,
            currency=result.currency,
            product_url=result.product_url,
        )
    )


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
    is_fulfilled = await item_service.get_is_fulfilled(db, item.id)
    return WishItemSingleResponse(data=item_service.build_item_response(item, is_reserved, is_fulfilled))


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
    is_fulfilled = await item_service.get_is_fulfilled(db, updated.id)
    return WishItemSingleResponse(data=item_service.build_item_response(updated, is_reserved, is_fulfilled))


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
    is_fulfilled = await item_service.get_is_fulfilled(db, updated.id)
    return WishItemSingleResponse(data=item_service.build_item_response(updated, is_reserved, is_fulfilled))
