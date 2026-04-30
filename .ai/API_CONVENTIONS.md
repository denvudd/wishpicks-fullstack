# API Conventions

All API endpoints must follow these conventions without exception. When in doubt, refer to this document before writing a router or schema.

---

## Base URL

All endpoints are prefixed with `/api`. The frontend uses `NUXT_PUBLIC_API_BASE_URL` as the base, so never include the domain in route definitions.

---

## Response Shape

Every response — success or error — follows the same top-level envelope.

### Success

```json
{
  "data": { ... }
}
```

For lists, always include pagination metadata:

```json
{
  "data": {
    "items": [ ... ],
    "total": 42,
    "limit": 20,
    "offset": 0
  }
}
```

### Error

```json
{
  "error": {
    "code": "WISHLIST_NOT_FOUND",
    "message": "Wishlist with this ID does not exist."
  }
}
```

- `code` — machine-readable, SCREAMING_SNAKE_CASE, used by the frontend to handle errors programmatically
- `message` — human-readable, in English, safe to display in logs (never include sensitive data)
- Never return raw Python exceptions or stack traces in production responses
- Validation errors (422) follow the same envelope with `code: "VALIDATION_ERROR"` and a `details` array

### Validation error shape

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [
      { "field": "email", "message": "Invalid email format." },
      { "field": "password", "message": "Must be at least 8 characters." }
    ]
  }
}
```

---

## HTTP Status Codes

| Situation | Code |
|---|---|
| Successful read | 200 |
| Successful create | 201 |
| Successful delete (no body) | 204 |
| Validation failed | 422 |
| Not authenticated | 401 |
| Authenticated but not authorized | 403 |
| Resource not found | 404 |
| Conflict (duplicate, already reserved) | 409 |
| Rate limit exceeded | 429 |
| Server error | 500 |

Use 403 when the user is authenticated but does not own the resource. Use 401 only when there is no valid session at all.

---

## Naming

### Endpoints

- Lowercase, hyphen-separated path segments: `/api/wish-items`, not `/api/wishItems`
- Resource names are plural nouns: `/api/wishlists`, `/api/items`
- Actions that are not CRUD use a verb suffix: `/api/items/:id/reserve`, `/api/items/parse-url`
- Nested routes only one level deep: `/api/wishlists/:id/items` is fine, `/api/wishlists/:id/items/:itemId/images` is not

### Fields in request/response bodies

- All field names are `snake_case`
- Boolean fields are prefixed with `is_` or `has_`: `is_public`, `is_reserved`, `is_surprise`
- Timestamps are named `created_at`, `updated_at`, `expires_at` — always ISO 8601 UTC strings
- Foreign key fields use the full name: `wishlist_id`, `user_id`, not `wishlist`, `user`
- IDs are always strings (UUID) in JSON, never integers

### Query parameters

- Pagination: `limit` (default 20, max 100) and `offset` (default 0)
- Filtering: `?event_type=birthday`, `?is_public=true`
- Sorting: `?sort=created_at&order=desc`

---

## Authentication

- Protected endpoints read the `access_token` HTTP-only cookie automatically via FastAPI dependency `get_current_user`
- If the token is missing or invalid → 401 with `code: "NOT_AUTHENTICATED"`
- If the token is valid but the user doesn't own the resource → 403 with `code: "FORBIDDEN"`
- Public endpoints that behave differently when logged in use `optional_current_user` dependency — this returns `User | None` without raising on missing token

---

## Ownership Checks

Every mutating endpoint (PATCH, DELETE, POST on a nested resource) must verify ownership explicitly in the service layer. Pattern:

1. Fetch the resource by ID
2. If not found → raise 404
3. If `resource.user_id != current_user.id` → raise 403
4. Proceed with the operation

Never rely on filtering by `user_id` in the query as a substitute for an ownership check — it silently returns empty instead of 404/403.

---

## Sensitive Data Rules

These fields must **never** appear in any API response, regardless of endpoint or caller:

- `password_hash`
- `reserver_id` (on any endpoint accessible by the wishlist owner)
- `reserver_name` (same rule)
- `jti` (refresh token ID)
- Any internal database sequence or auto-increment value

The serialization layer (Pydantic response schemas) is the enforcement point. Define separate response schemas for owner view vs. guest view where needed.

---

## Idempotency

- `POST /api/saved/wishlists/:id` — saving an already-saved wishlist returns 200, not 409
- `DELETE /api/saved/wishlists/:id` — removing a non-saved wishlist returns 204, not 404
- `POST /api/items/:id/reserve` — reserving an already-reserved item returns 409 with `code: "ALREADY_RESERVED"`
- `DELETE /api/items/:id/reserve` — cancelling a non-existent reservation returns 204

---

## Pydantic Schema Organization

Each domain has three schema files or three sections in one file:

- `Request` schemas — validate incoming data (used in router function signatures)
- `Response` schemas — define outgoing data (used in `response_model=`)
- Never use the ORM model directly as a response model

Naming convention:
- `WishlistCreate`, `WishlistUpdate` — request schemas
- `WishlistResponse`, `WishlistListResponse` — response schemas
- `WishlistGuestResponse` — guest-safe variant (strips sensitive fields)