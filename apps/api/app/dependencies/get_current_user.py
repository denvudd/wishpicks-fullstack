import uuid

from fastapi import Cookie, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_token
from app.dependencies.get_db import get_db
from app.models.user import User

_NOT_AUTHENTICATED = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail={"error": {"code": "NOT_AUTHENTICATED", "message": "Authentication required."}},
)


async def get_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not access_token:
        raise _NOT_AUTHENTICATED
    try:
        payload = decode_token(access_token)
    except JWTError:
        raise _NOT_AUTHENTICATED
    if payload.get("type") != "access":
        raise _NOT_AUTHENTICATED
    user_id = payload.get("sub")
    if not user_id:
        raise _NOT_AUTHENTICATED
    user = await db.scalar(select(User).where(User.id == uuid.UUID(user_id)))
    if not user or not user.is_active:
        raise _NOT_AUTHENTICATED
    return user


async def optional_current_user(
    access_token: str | None = Cookie(default=None),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    if not access_token:
        return None
    try:
        return await get_current_user(access_token=access_token, db=db)
    except HTTPException:
        return None
