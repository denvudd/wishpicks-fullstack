# Saved Wishlists & Items (API)

## Description

Implemented the full API for Phase 3 saved/copy features:
- Save/unsave wishlists (bookmark)
- Copy a wish item from someone else's wishlist into your own (with custom priority and notes), recording the source as a bookmark
- Added `preview_images` field (up to 3 item image URLs) to all wishlist responses to support the new card design

No DB migration was needed — `saved_wishlists` and `saved_items` tables already existed from the initial schema.

---

## Session Log

### Schema changes

- Modified `app/schemas/wishlists.py`:
  - Added `preview_images: list[str]` to `WishlistResponse`

- Replaced `app/schemas/saved.py` with full schemas:
  - `SavedWishlistResponse` — includes `owner_display_name`, `preview_images`, `saved_at`
  - `SavedWishlistListData` / `SavedWishlistListResponse` / `SavedWishlistSingleResponse`
  - `CopyItemRequest` — `wishlist_id`, `priority`, `notes`
  - `SavedItemResponse` — original source item fields + `saved_at`
  - `SavedItemListData` / `SavedItemListResponse`

### Service changes

- Modified `app/services/wishlists.py`:
  - Added `_fetch_preview_images(db, wishlist_ids)` — batch query; groups up to 3 image URLs per wishlist in Python
  - Added `get_preview_images(db, wishlist_id)` — single-wishlist variant, `LIMIT 3`
  - Updated `list_wishlists` return type to `tuple[list[tuple[Wishlist, int, list[str]]], int]`

- Replaced `app/services/saved.py` with full implementation:
  - `list_saved_wishlists` — joins `saved_wishlists → wishlists → users` with `selectinload(Wishlist.owner)` to avoid lazy-load errors; calls `_fetch_preview_images`
  - `save_wishlist` — 404 if not found, 403 if own, 409 if already saved; eager-loads `owner`
  - `unsave_wishlist` — checks `rowcount` for 404
  - `list_saved_items` — joins `saved_items → wish_items`
  - `copy_and_save_item` — checks source ownership (403 if own), target ownership (404 if not theirs), creates `WishItem` copy, inserts into `saved_items` with `ON CONFLICT DO NOTHING`
  - `unsave_item` — removes bookmark only; does not touch the copied item

### Router changes

- Modified `app/routers/wishlists.py`:
  - `_build_response` now takes `preview_images: list[str]` as third arg
  - All endpoints updated: `list_wishlists` unpacks 3-tuple; `get_wishlist` / `update_wishlist` call `get_preview_images`; `create_wishlist` passes `[]`

- Replaced `app/routers/saved.py` with 6 endpoints:
  - `GET /api/saved/wishlists`
  - `POST /api/saved/wishlists/:id`
  - `DELETE /api/saved/wishlists/:id`
  - `GET /api/saved/items`
  - `POST /api/saved/items/:id`
  - `DELETE /api/saved/items/:id`

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Save item = copy, not bookmark-only | Creates new `WishItem` in user's wishlist; records source in `saved_items` | User explicitly confirmed this; the item shows up in their own wishlists |
| `saved_items` ON CONFLICT DO NOTHING | Copying same source item twice creates two copies but only one bookmark | Prevents 409 errors while still tracking what the user saved |
| Preview images via second query | Fetch all wishlist IDs first, then one batch query; group in Python | Simpler than lateral joins / window functions in SQLAlchemy async; still O(2) queries not N+1 |
| `selectinload(Wishlist.owner)` | Eager load in `list_saved_wishlists` and `save_wishlist` | Async SQLAlchemy raises MissingGreenlet on lazy relationship access |
| `_fetch_preview_images` imported from `services.wishlists` | Used by both `wishlists` service and `saved` service | No circular import; `wishlists` does not import `saved` |
