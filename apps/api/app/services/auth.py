import uuid
from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token
from app.core.settings import settings
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def _verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


async def _issue_tokens(db: AsyncSession, user_id: uuid.UUID) -> tuple[str, str]:
    jti = uuid.uuid4()
    expires_at = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db.add(RefreshToken(jti=jti, user_id=user_id, expires_at=expires_at))
    await db.flush()
    return create_access_token(user_id), create_refresh_token(user_id, jti)


async def register(db: AsyncSession, data: RegisterRequest) -> tuple[User, str, str]:
    existing = await db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "EMAIL_ALREADY_EXISTS",
                    "message": "Email is already registered.",
                }
            },
        )
    user = User(
        email=data.email,
        password_hash=_hash_password(data.password),
        display_name=data.display_name,
    )
    db.add(user)
    await db.flush()
    access_token, refresh_token = await _issue_tokens(db, user.id)
    await db.commit()
    await db.refresh(user)
    return user, access_token, refresh_token


async def login(db: AsyncSession, data: LoginRequest) -> tuple[User, str, str]:
    user = await db.scalar(select(User).where(User.email == data.email))
    _invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
            }
        },
    )
    if not user or not user.password_hash:
        raise _invalid
    if not _verify_password(data.password, user.password_hash):
        raise _invalid
    access_token, refresh_token = await _issue_tokens(db, user.id)
    await db.commit()
    await db.refresh(user)
    return user, access_token, refresh_token


async def logout(db: AsyncSession, jti_str: str | None) -> None:
    if not jti_str:
        return
    try:
        jti = uuid.UUID(jti_str)
    except ValueError:
        return
    token_record = await db.get(RefreshToken, jti)
    if token_record:
        token_record.revoked = True
        await db.commit()


async def get_me(db: AsyncSession, user_id: uuid.UUID) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "NOT_AUTHENTICATED",
                    "message": "Authentication required.",
                }
            },
        )
    return user


async def refresh_tokens(
    db: AsyncSession,
    redis,
    refresh_token_str: str,
) -> tuple[User, str, str]:
    from jose import JWTError

    from app.core.security import decode_token

    _invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "NOT_AUTHENTICATED",
                "message": "Authentication required.",
            }
        },
    )
    _stolen = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "SESSION_REVOKED",
                "message": "Session revoked. Please log in again.",
            }
        },
    )

    try:
        payload = decode_token(refresh_token_str)
    except JWTError:
        raise _invalid

    if payload.get("type") != "refresh":
        raise _invalid

    jti_str = payload.get("jti")
    user_id_str = payload.get("sub")
    if not jti_str or not user_id_str:
        raise _invalid

    jti = uuid.UUID(jti_str)
    user_id = uuid.UUID(user_id_str)

    # Fast-check Redis first (graceful degradation if Redis is down)
    if redis:
        try:
            is_revoked = await redis.get(f"revoked_jti:{jti}")
            if is_revoked:
                await _revoke_all_user_tokens(db, redis, user_id)
                raise _stolen
        except HTTPException:
            raise
        except Exception:
            pass  # Redis failure → fall through to DB check

    token_record = await db.get(RefreshToken, jti)
    if not token_record:
        raise _invalid
    if token_record.revoked:
        await _revoke_all_user_tokens(db, redis, user_id)
        raise _stolen

    # Valid token — rotate: mark old JTI revoked
    token_record.revoked = True
    await db.flush()

    # Store old JTI in Redis with remaining TTL for fast rejection
    if redis:
        try:
            remaining = int(
                (
                    token_record.expires_at.replace(tzinfo=UTC) - datetime.now(UTC)
                ).total_seconds()
            )
            if remaining > 0:
                await redis.setex(f"revoked_jti:{jti}", remaining, "1")
        except Exception:
            pass

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise _invalid

    access_token, new_refresh_token = await _issue_tokens(db, user_id)
    await db.commit()
    await db.refresh(user)
    return user, access_token, new_refresh_token


async def _revoke_all_user_tokens(db: AsyncSession, redis, user_id: uuid.UUID) -> None:
    from sqlalchemy import update

    await db.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False))
        .values(revoked=True)
    )
    await db.commit()
