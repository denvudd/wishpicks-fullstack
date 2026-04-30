# Database Conventions

All database work — models, migrations, queries — must follow these conventions. Read before creating any model or migration.

---

## General Rules

- Database: PostgreSQL (Neon in production, Docker container in dev)
- ORM: SQLAlchemy 2.x with async engine (`asyncpg` driver)
- Migrations: Alembic only — never use `Base.metadata.create_all()` anywhere
- All schema changes go through a migration file, including index additions and column renames
- Never write raw SQL in application code — use SQLAlchemy ORM or Core expressions

---

## Naming

### Tables

- Plural, `snake_case`: `users`, `wishlists`, `wish_items`, `refresh_tokens`, `saved_wishlists`, `saved_items`
- Junction / association tables named as `noun_noun`: `saved_wishlists`, `saved_items`
- No prefixes (no `tbl_`, no `wp_`)

### Columns

- `snake_case` throughout
- Primary key: always `id`
- Foreign keys: `{referenced_table_singular}_id` — e.g. `user_id`, `wishlist_id`, `item_id`
- Boolean columns: prefixed with `is_` or `has_` — `is_active`, `is_public`, `is_revoked`
- Timestamp columns: `created_at`, `updated_at`, `expires_at`, `deleted_at`
- Never abbreviate column names — `description` not `desc`, `position` not `pos`

### Indexes

- Explicit name format: `ix_{table}_{column}` for single-column, `ix_{table}_{col1}_{col2}` for composite
- Unique constraints: `uq_{table}_{column}`
- Foreign key indexes: `ix_{table}_{fk_column}` — always add an index on every FK column

---

## Primary Keys

All tables use UUID v4 as primary key. No auto-increment integers anywhere.

```python
# Standard PK definition in every model
id: Mapped[uuid.UUID] = mapped_column(
    UUID(as_uuid=True),
    primary_key=True,
    default=uuid.uuid4,
)
```

Exception: composite primary keys on junction tables (`saved_wishlists`, `saved_items`) use two UUID foreign keys as the composite PK — no separate `id` column.

---

## Timestamps

Every table except junction tables must have `created_at` and `updated_at`.

- `created_at` — set once on insert, never updated
- `updated_at` — updated automatically on every row change via SQLAlchemy `onupdate`
- Both are `TIMESTAMPTZ` (timezone-aware) — never `TIMESTAMP WITHOUT TIME ZONE`
- All timestamps stored and returned in UTC

```python
# Standard timestamp columns
created_at: Mapped[datetime] = mapped_column(
    TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
)
updated_at: Mapped[datetime] = mapped_column(
    TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
)
```

---

## Nullable vs. Not Null

- Default to `NOT NULL` — add `nullable=True` only with explicit justification
- Optional fields that have no meaningful default: `nullable=True` (e.g. `description`, `avatar_url`, `price`)
- Fields with a domain default: `NOT NULL` with `server_default` or `default` (e.g. `is_public`, `priority`, `currency`)
- Foreign keys to optional relationships: `nullable=True` (e.g. `reserver_id` on reservations)

---

## Enums

Use Python `enum.Enum` + SQLAlchemy `Enum` type for constrained string columns.

- Define the enum class in `app/models/enums.py`
- Use `native_enum=False` to store as VARCHAR — avoids Postgres enum type migration complexity
- Naming: `EventType`, `ItemPriority` — PascalCase

---

## Indexes to Always Add

| Scenario | Index |
|---|---|
| Every foreign key column | Single-column index |
| `slug` on wishlists | Unique index |
| `email` on users | Unique index |
| `google_id` on users | Unique index (partial: `WHERE google_id IS NOT NULL`) |
| `jti` on refresh_tokens | Already PK, no extra index needed |
| `item_id` on reservations | Already unique constraint, covers index |
| `expires_at` on refresh_tokens | Index for cleanup queries |

---

## SQLAlchemy Model Structure

```
app/models/
├── __init__.py       # exports all models so Alembic can discover them
├── base.py           # declarative Base, shared mixins (TimestampMixin, UUIDMixin)
├── enums.py          # all Enum definitions
├── user.py
├── wishlist.py
├── wish_item.py
├── reservation.py
├── refresh_token.py
└── saved.py          # SavedWishlist, SavedItem
```

- One model per file
- All models imported in `__init__.py` — required for Alembic autogenerate to detect them
- Relationships defined with `relationship()` using `back_populates` — always bidirectional
- Lazy loading disabled — use `selectinload` or `joinedload` explicitly in queries

---

## Alembic Workflow

### Creating a migration

```bash
# Always review the generated file before applying
uv run alembic revision --autogenerate -m "short_description_of_change"

# Then inspect migrations/versions/{hash}_short_description_of_change.py
# Verify the upgrade() and downgrade() functions are correct

# Apply
uv run alembic upgrade head
```

### Rules for migration files

- Every `upgrade()` must have a working `downgrade()`
- Never edit an already-applied migration file — create a new one
- Never delete a migration file
- Migration messages are lowercase, underscore-separated, descriptive: `add_slug_to_wishlists`, `add_index_on_refresh_tokens_expires_at`
- Do not put data migrations (UPDATE, INSERT) in the same file as schema migrations — separate files

### What Alembic autogenerate does NOT detect

- Index changes on existing columns (must be added manually)
- Partial indexes (`WHERE` clause)
- Check constraints
- Changes inside Postgres enum types (avoid native enums for this reason)

Always review the autogenerated file — do not apply blindly.

---

## Query Patterns

### Never do N+1 queries

When fetching a wishlist with its items, use eager loading:

```python
# Correct — one query with join
stmt = select(Wishlist).options(selectinload(Wishlist.items)).where(Wishlist.id == wishlist_id)

# Wrong — triggers N+1
wishlist = await session.get(Wishlist, wishlist_id)
items = wishlist.items  # lazy load fires here
```

### Ownership check pattern

```python
# Always fetch first, then check ownership — never filter by user_id as a security mechanism
result = await session.get(Wishlist, wishlist_id)
if result is None:
    raise NotFoundException("WISHLIST_NOT_FOUND")
if result.user_id != current_user.id:
    raise ForbiddenException("FORBIDDEN")
```

### Pagination

```python
stmt = select(Wishlist).where(...).order_by(Wishlist.created_at.desc()).limit(limit).offset(offset)
count_stmt = select(func.count()).select_from(Wishlist).where(...)
```

---

## Soft Delete

Not used at MVP. All deletes are hard deletes with cascade. If soft delete is needed later, it will be added as a `deleted_at TIMESTAMPTZ` column with a migration — do not pre-emptively add it.

---

## Redis Conventions

Redis is used for two purposes only:

| Purpose | Key pattern | TTL |
|---|---|---|
| URL parser cache | `parse:{normalized_url_hash}` | 1 hour |
| Revoked JTI fast-check | `revoked_jti:{jti}` | Remaining token lifetime |
| Rate limit counters | Managed by `slowapi` automatically | Per-window |

- Keys are namespaced with a prefix and colon separator
- For URL cache: hash the normalized URL (lowercase, stripped) with SHA-256 — do not use the raw URL as a key
- Redis is a cache and a fast-check layer — the source of truth for revoked tokens is the `refresh_tokens` table in Postgres
- On Redis connection failure: log the error, fall through to the source of truth — never crash the request