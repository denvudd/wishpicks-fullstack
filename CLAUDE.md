# Wishpicks — Claude Code Instructions

Read this file fully before doing anything. Then read `docs/ARCHITECTURE.md`.

---

## Project Structure

```
wishpicks/
├── apps/
│   ├── web/                  # Nuxt 3 frontend
│   │   ├── pages/
│   │   ├── components/
│   │   ├── composables/
│   │   ├── stores/           # Pinia stores
│   │   ├── locales/          # i18n translation files (uk.json, en.json)
│   │   └── server/           # Nuxt server routes (if any)
│   └── api/                  # FastAPI backend
│       ├── app/
│       │   ├── routers/      # One file per domain (auth, wishlists, items, etc.)
│       │   ├── models/       # SQLAlchemy ORM models
│       │   ├── schemas/      # Pydantic request/response schemas
│       │   ├── services/     # Business logic (no DB queries in routers)
│       │   ├── dependencies/ # FastAPI deps (get_current_user, get_db, etc.)
│       │   ├── middleware/   # CORS, security headers, CSRF
│       │   └── core/         # Config (settings.py), DB engine, Redis client
│       ├── migrations/       # Alembic migrations
│       └── pyproject.toml
├── docs/
│   ├── ARCHITECTURE.md       # Full product and system spec — read before implementing any feature
│   ├── API_CONVENTIONS.md    # API response shapes, naming, status codes
│   └── DB_CONVENTIONS.md     # DB naming, migration rules, indexing
├── docker-compose.yml
└── .env.example
```

---

## Local Development

```bash
# Start everything
docker-compose up

# Services and ports
# Frontend:  http://localhost:3000
# Backend:   http://localhost:8000
# API docs:  http://localhost:8000/docs
# Postgres:  localhost:5432
# Redis:     localhost:6379
```

```bash
# Backend — inside apps/api/
uv run alembic upgrade head          # run migrations
uv run alembic revision --autogenerate -m "description"  # create migration
uv run pytest                        # run tests
uv run ruff check .                  # lint
uv run ruff format .                 # format

# Frontend — inside apps/web/
npm dev                             # dev server
npm build                           # production build
npm lint                            # lint
```

---

## Architecture Rules

**Read `docs/ARCHITECTURE.md` before implementing any feature.** All product decisions, data model, API structure, auth flow, and business rules are defined there. Do not deviate.

Key constraints to remember:
- All public-facing IDs are UUID v4 — never expose auto-increment integers
- Tokens live in HTTP-only cookies only — never in response body or localStorage
- Owner never sees reserver identity — enforced at serializer level, not frontend
- All business logic lives in `services/` — routers only handle HTTP concerns
- All DB changes go through Alembic migrations — never raw SQL or `create_all()`

---

## Backend Conventions

- One router file per domain: `auth.py`, `wishlists.py`, `items.py`, `reservations.py`, `saved.py`, `media.py`
- Router functions are thin — validate input, call service, return response
- Services handle all logic and DB interaction
- Dependencies in `dependencies/` — `get_current_user`, `get_db`, `get_redis`, `optional_current_user`
- `optional_current_user` for public endpoints that behave differently when authenticated (e.g. shared wishlist, reservation)
- Settings loaded from `.env` via `pydantic-settings` — access via `from app.core.config import settings`
- Never import `os.environ` directly anywhere

## Frontend Conventions

- One Pinia store per domain: `useAuthStore`, `useWishlistStore`, `useItemStore`, `useSavedStore`
- All API calls go through composables in `composables/api/` — never call `$fetch` directly from a component
- Auth composable (`useAuth`) is the only place that reads/writes auth state
- All user-facing strings go in `locales/uk.json` and `locales/en.json` — no hardcoded text in components
- Components are in `components/` with subdirectories by domain: `components/wishlist/`, `components/items/`, etc.

---

## Do Not Do (Without Explicit Confirmation)

- Do not drop or modify existing migration files
- Do not run `alembic downgrade` on any environment
- Do not add `*` to CORS allowed origins
- Do not store any token, secret, or credential in code — use env vars
- Do not use `Base.metadata.create_all()` — migrations only
- Do not add new infrastructure dependencies (new services, new hosted tools) without checking cost
- Do not change the auth cookie strategy (HTTP-only JWT) — this is a security decision
- Do not skip Pydantic validation on any endpoint input

---

## References

- Full product spec and all decisions: `docs/ARCHITECTURE.md`
- API response format and naming: `docs/API_CONVENTIONS.md`
- Database naming and migration rules: `docs/DB_CONVENTIONS.md`
- Environment variables: `.env.example`