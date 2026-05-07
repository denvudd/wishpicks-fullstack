from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.core.settings import settings
from app.middleware.cors import add_cors_middleware
from app.middleware.csrf import add_csrf_middleware
from app.middleware.security_headers import add_security_headers_middleware
from app.routers import auth, items, media, reservations, saved, users, wishlists

app = FastAPI(
    title="Wishpicks API",
    version="0.1.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    openapi_url="/openapi.json" if settings.ENVIRONMENT != "production" else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        body = detail
    else:
        body = {"error": {"code": "HTTP_ERROR", "message": str(detail)}}
    return JSONResponse(status_code=exc.status_code, content=body)


add_cors_middleware(app)
add_security_headers_middleware(app)
add_csrf_middleware(app)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(wishlists.router, prefix="/api/wishlists", tags=["wishlists"])
app.include_router(items.router, prefix="/api/items", tags=["items"])
app.include_router(reservations.router, prefix="/api", tags=["reservations"])
app.include_router(saved.router, prefix="/api/saved", tags=["saved"])
app.include_router(media.router, prefix="/api/media", tags=["media"])


@app.get("/api/health", tags=["health"])
async def health():
    return {"data": {"status": "ok", "environment": settings.ENVIRONMENT}}
