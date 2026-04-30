from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.settings import settings

_SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method not in _SAFE_METHODS and settings.ENVIRONMENT == "production":
            origin = request.headers.get("origin") or request.headers.get("referer", "")
            if not origin.startswith(settings.FRONTEND_URL):
                return JSONResponse(
                    status_code=403,
                    content={"error": {"code": "FORBIDDEN", "message": "Invalid origin."}},
                )
        return await call_next(request)


def add_csrf_middleware(app: FastAPI) -> None:
    app.add_middleware(CSRFMiddleware)
