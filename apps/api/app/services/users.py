from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.users import UserUpdateRequest


async def update_profile(db: AsyncSession, user: User, data: UserUpdateRequest) -> User:
    if "username" in data.model_fields_set and data.username is not None:
        existing = await db.scalar(select(User).where(User.username == data.username, User.id != user.id))
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "USERNAME_TAKEN",
                        "message": "This username is already taken.",
                    }
                },
            )

    for field in data.model_fields_set:
        setattr(user, field, getattr(data, field))

    await db.commit()
    await db.refresh(user)
    return user


async def delete_account(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()
