import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt

from app.core.settings import settings

_ALGORITHM = "HS256"


def create_access_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(UTC) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "access"},
        settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )


def create_refresh_token(user_id: uuid.UUID, jti: uuid.UUID) -> str:
    expire = datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "jti": str(jti), "exp": expire, "type": "refresh"},
        settings.SECRET_KEY,
        algorithm=_ALGORITHM,
    )


def decode_token(token: str) -> dict:
    """Decodes and validates token signature + expiry. Raises JWTError on failure."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[_ALGORITHM])
