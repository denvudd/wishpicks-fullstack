# Wishpicks API

FastAPI backend for the Wishpicks wishlist platform.

## Stack

| Concern | Technology |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.x (async) |
| DB driver | asyncpg |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT via python-jose, bcrypt |
| Rate limiting | slowapi + Redis |
| Cache | Redis (Upstash in prod) |
| Package manager | uv |

## Local development

All services run through Docker Compose from the repo root:

```bash
# Start everything (Postgres + Redis + API + Web)
docker-compose up

# API is available at http://localhost:8000
# Swagger UI at http://localhost:8000/docs  (development only)
```

The API container mounts `./apps/api` as a volume and runs uvicorn with `--reload`, so file changes are picked up immediately without rebuilding.

## Environment variables

Copy `.env.example` (repo root) and fill in the values. The API container reads from that file via `env_file` in docker-compose.

| Variable | Description |
|---|---|
| `DATABASE_URL` | asyncpg connection string — use `postgres` as host inside Docker |
| `SECRET_KEY` | JWT signing secret, min 32 chars. Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default: `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default: `30` |
| `GOOGLE_CLIENT_ID` | Google OAuth app |
| `GOOGLE_CLIENT_SECRET` | Google OAuth app |
| `GOOGLE_REDIRECT_URI` | Must match exactly what's registered in Google Console |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account |
| `CLOUDINARY_API_KEY` | Cloudinary account |
| `CLOUDINARY_API_SECRET` | Cloudinary account |
| `FRONTEND_URL` | Used for CORS and CSRF validation |
| `ENVIRONMENT` | `development` or `production` |
| `REDIS_URL` | Use `redis://redis:6379` inside Docker |

## Project structure

```
app/
├── core/
│   ├── settings.py        # Typed config via pydantic-settings
│   ├── db.py              # Async SQLAlchemy engine + session factory
│   ├── redis.py           # Redis client with graceful degradation
│   ├── security.py        # JWT create/decode utilities
│   └── limiter.py         # slowapi limiter instance
├── models/
│   ├── base.py            # DeclarativeBase, UUIDMixin, TimestampMixin
│   └── enums.py           # EventType, ItemPriority
├── schemas/               # Pydantic request/response schemas (one file per domain)
├── services/              # Business logic
├── routers/               # HTTP layer — one file per domain
├── dependencies/
│   ├── get_db.py          # Yields AsyncSession
│   ├── get_redis.py       # Yields Redis | None
│   └── get_current_user.py  # get_current_user / optional_current_user
├── middleware/
│   ├── cors.py
│   ├── csrf.py            # Origin/Referer validation (production only)
│   └── security_headers.py
└── main.py                # App factory, middleware, routers
migrations/
└── versions/              # Alembic migration files
```

## Alembic migrations

```bash
# Run inside the api container
docker exec wishpicks-api-1 uv run alembic upgrade head

# Generate a new migration after model changes
docker exec wishpicks-api-1 uv run alembic revision --autogenerate -m "describe_the_change"
# Always review the generated file before applying — autogenerate misses partial indexes,
# check constraints, and changes inside Postgres enum types.

# Check current migration state
docker exec wishpicks-api-1 uv run alembic current
```

## Linting and formatting

```bash
docker exec wishpicks-api-1 uv run ruff check app/
docker exec wishpicks-api-1 uv run ruff format app/
```

Or locally if you have uv installed:

```bash
cd apps/api
uv run ruff check app/
uv run ruff format app/
```

## Authentication

Tokens live **only in HTTP-only cookies** — never in the response body or localStorage.

| Cookie | Lifetime | Path |
|---|---|---|
| `access_token` | 15 min | `/` |
| `refresh_token` | 30 days | `/api/auth/refresh` |

**Refresh token rotation:** every `/api/auth/refresh` call issues a new pair and revokes the old JTI in the DB. If a revoked JTI is replayed (theft detection), all sessions for that user are immediately revoked.

## Key architecture rules

- **All business logic in `services/`** — routers only handle HTTP concerns (cookies, status codes, response models).
- **Never expose auto-increment IDs** — all public-facing IDs are UUID v4.
- **All DB changes via Alembic** — never use `Base.metadata.create_all()` in application code.
- **Owner never sees reserver identity** — enforced at the serialization layer in response schemas, not in the frontend.
- **Redis failures are non-fatal** — all Redis operations fall through gracefully; Postgres is the source of truth.
- **Swagger/OpenAPI disabled in production** — set `ENVIRONMENT=production` to disable `/docs`, `/redoc`, `/openapi.json`.

## API response format

All responses follow the same envelope:

```json
// Success
{ "data": { ... } }

// Error
{ "error": { "code": "SCREAMING_SNAKE_CASE", "message": "Human-readable description." } }

// Validation error
{ "error": { "code": "VALIDATION_ERROR", "message": "...", "details": [...] } }
```

## Rate limits

| Endpoint | Limit |
|---|---|
| `POST /api/auth/register` | 3 / minute / IP |
| `POST /api/auth/login` | 5 / minute / IP |
| All other auth endpoints | 10 / minute / IP |
| `POST /api/items/parse-url` | 10 / minute / authenticated user |

## Rebuilding the Docker image

Required when `pyproject.toml` dependencies change:

```bash
docker-compose up -d --build api
```
