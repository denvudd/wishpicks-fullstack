# Wish Item Extra Images (API)

## Description

Added support for up to 5 additional images per wish item, stored as a JSON array column `images` on `wish_items`. Includes Pydantic URL validators, an Alembic migration, and service/response wiring. The existing `PATCH /api/items/:id` endpoint handles all writes — no new routes needed.

---

## Session Log

### Migration

- Created `apps/api/migrations/versions/2b85e80489b2_add_images_to_wish_items.py`:
  - `upgrade`: `op.add_column('wish_items', sa.Column('images', sa.JSON(), nullable=True))`
  - `downgrade`: `op.drop_column('wish_items', 'images')`
  - Applied via `docker exec wishpicks-api-1 uv run alembic upgrade head`

### Model

- Modified `apps/api/app/models/wish_item.py`:
  - Added `images: Mapped[list[str] | None] = mapped_column(JSON, nullable=True)` after `tags` — same JSON column pattern already used by `tags`

### Schemas

- Modified `apps/api/app/schemas/items.py`:
  - Added module-level `_url_adapter = TypeAdapter(AnyHttpUrl)` (reuses the same pattern as `users.py`)
  - Added `images: list[str] | None = None` to `WishItemCreate` and `WishItemUpdate`
  - Added `image_url_is_http` field validator to both — validates the primary image URL as a proper HTTP/HTTPS URL
  - Added `images_are_http` field validator — validates every URL in the `images` list
  - Added `images_max_five` field validator (mode `after`) — raises `ValueError` if `len(images) > 5`
  - Added `images: list[str] | None` to `WishItemResponse`

### Service

- Modified `apps/api/app/services/items.py`:
  - Added `images=data.images` to `WishItem(...)` constructor in `create_item`
  - Added `images=item.images` to `WishItemResponse(...)` constructor in `build_item_response`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Storage | JSON column (same as `tags`) | Max 5 items — no N+1 risk, no join overhead, zero extra schema complexity |
| Write endpoint | Existing `PATCH /api/items/:id` | Frontend always sends the full array on save; no need for a dedicated endpoint |
| Validation | Two `field_validator`s on `images` | Separate URL format check (mode `before`) and max-count check (mode `after`) for clear error messages |
| Primary `image_url` validation | Same `_url_adapter` pattern as `avatar_url` | Consistent URL validation across the codebase |
