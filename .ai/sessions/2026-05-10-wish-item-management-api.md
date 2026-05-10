# Wish Item Management (API)

## Description

Implemented the full wish item CRUD API: schemas, service layer, and router. Added support for price ranges, tags, notes, priority levels, and reservation tracking.

## Session Log

### Schemas

1. Created `apps/api/app/schemas/items.py`:
   - `WishItemCreate` — full create body with price range validation (`price_max >= price_min`)
   - `WishItemUpdate` — partial update (all fields optional), same price validation
   - `WishItemPositionUpdate` — single `position` field with `ge=0`
   - `WishItemResponse` — full item response including computed `is_reserved`
   - `WishItemListData`, `WishItemListResponse`, `WishItemSingleResponse` — envelope wrappers

### Service

2. Created `apps/api/app/services/items.py`:
   - `list_items` — paginated query with correlated `is_reserved` subquery, ordered by `position`
   - `create_item` — auto-assigns `position = max + 1` (or 0 for first item)
   - `get_item_by_id` — fetch by ID, raises 404 if not found (no ownership check)
   - `get_item_for_owner` — fetch by ID + verify wishlist ownership, raises 403 if mismatch
   - `update_item` — applies only fields present in `model_fields_set`
   - `delete_item`, `update_position`
   - `get_is_reserved` — counts reservations for item
   - `build_item_response` — assembles `WishItemResponse` from ORM model + reservation flag

### Router

3. Created `apps/api/app/routers/items.py` (mounted at `/api/items`):
   - `GET /{item_id}` — get single item (auth required, no ownership check)
   - `PATCH /{item_id}` — update item (owner only)
   - `DELETE /{item_id}` — delete item (owner only), 204
   - `PATCH /{item_id}/position` — reorder item (owner only)

4. Wishlist-scoped item routes in `apps/api/app/routers/wishlists.py`:
   - `GET /api/wishlists/{wishlist_id}/items` — paginated list
   - `POST /api/wishlists/{wishlist_id}/items` — create item in wishlist

## Session Outcomes

- Full wish item CRUD with ownership enforcement
- Price range stored as `Decimal` fields; currency defaults to `UAH`
- Priority stored as `ItemPriority` enum (0 = normal, 1 = high, 2 = must_have)
- `is_reserved` computed via correlated subquery — never stored directly
- Separate endpoints for owner mutations vs. public read (`get_item_by_id`)
