# Reservations & Fulfillment

## Description

Implemented the full reservation and fulfillment system: anonymous and authenticated reservations, cancellation, fulfillment toggling, shared wishlist public page, and owner fulfillment controls on the dashboard. Anonymous users receive a one-time `anon_token` stored in localStorage for subsequent cancel/fulfill actions.

---

## API Changes

### Migration

- Created `apps/api/migrations/versions/87b9897b317e_add_anon_token_to_reservations.py`
  - Adds `anon_token VARCHAR` (nullable, indexed) to `reservations` table

### Model

- Modified `apps/api/app/models/reservation.py`:
  - Added `anon_token: Mapped[str | None] = mapped_column(String, nullable=True, index=True)`

### Schemas

- Created `apps/api/app/schemas/reservations.py`:
  - `ReservationCreate` — body with optional `reserver_name: str | None`
  - `ReservationResponse` — includes `item_id`, `anon_token: str | None` (only non-null for anonymous reservations)
  - `ReservationSingleResponse` — envelope wrapper
  - `FulfillRequest` — `is_fulfilled: bool`

- Created `apps/api/app/schemas/shared.py`:
  - `MyReservation` — `{ anon_token: None }` (token never echoed back after creation)
  - `SharedItemResponse` — public item view: `is_reserved`, `is_fulfilled`, `my_reservation: MyReservation | None`, no reserver identity
  - `SharedWishlistSchema` — public wishlist metadata
  - `SharedWishlistData`, `SharedWishlistResponse` — response envelope

### Services

- Created `apps/api/app/services/reservations.py`:
  - `_get_item_and_wishlist(db, item_id)` — joins `WishItem` + `Wishlist`, raises 404 if not found
  - `_authorize_action(reservation, wishlist, current_user, anon_token)` — raises 403 unless: authenticated reserver, wishlist owner, or matching anon_token header
  - `create_reservation(db, item_id, body, current_user)` — enforces `reservation_mode`, requires `reserver_name` for anonymous, blocks duplicate reservations, generates `anon_token` UUID for anonymous users
  - `delete_reservation(db, item_id, current_user, anon_token)` — authorizes then deletes row
  - `fulfill_reservation(db, item_id, is_fulfilled, current_user, anon_token)` — authorizes then flips `is_fulfilled`

- Created `apps/api/app/services/shared.py`:
  - `get_shared_wishlist(db, slug, current_user)` — returns 404 for `visibility == 'private'`; outer-joins items with reservations; sets `my_reservation` for the authenticated reserver

### Routers

- Replaced stub `apps/api/app/routers/reservations.py` (mounted at `/api/items`):
  - `POST /{item_id}/reserve` — rate-limited 10/min, `optional_current_user`
  - `DELETE /{item_id}/reserve` — reads `X-Anon-Token` header, `optional_current_user`
  - `PATCH /{item_id}/reserve/fulfill` — reads `X-Anon-Token` header, `optional_current_user`

- Created `apps/api/app/routers/shared.py` (mounted at `/api/w`):
  - `GET /{slug}` — public, `optional_current_user`

- Modified `apps/api/app/main.py`:
  - Imported and registered `shared` and `reservations` routers

---

## Frontend Changes

### Types

- Modified `apps/web/types/api.ts` — appended:
  - `MyReservation`, `SharedItemResponse`, `SharedWishlistMeta`, `SharedWishlistData`, `SharedWishlistResponse`
  - `ReservationResponse`, `ReservationSingleResponse`

### Store

- Created `apps/web/stores/useReservationStore.ts`:
  - Persists `{ [itemId]: anonToken }` map in `localStorage` under key `wishpicks_reservation_tokens`
  - `load()` — reads from localStorage (call in `onMounted` only, client-side guard)
  - `getToken(itemId)`, `setToken(itemId, token)`, `clearToken(itemId)`

### Composables

- Created `apps/web/composables/api/useReservationsApi.ts`:
  - `reserve(itemId, name?)` — `POST /api/items/:id/reserve`
  - `cancel(itemId, anonToken?)` — `DELETE /api/items/:id/reserve`, sends `X-Anon-Token` header if provided
  - `fulfill(itemId, isFulfilled, anonToken?)` — `PATCH /api/items/:id/reserve/fulfill`, sends `X-Anon-Token` header if provided
  - **Note:** must be explicitly imported (`import { useReservationsApi } from '~/composables/api/useReservationsApi'`) — Nuxt does not auto-import from `composables/api/` subdirectories

- Created `apps/web/composables/useSharedWishlist.ts`:
  - `useFetch` with `MaybeRefOrGetter<string>` slug for SSR compatibility
  - Returns `{ wishlist, items, pending, error }`

### Components

- Created `apps/web/components/shared/ItemCard.vue`:
  - Props: `item: SharedItemResponse`, `reservationMode: ReservationMode`, `anonToken?: string`, `isAuthenticated: boolean`
  - `isReservedByMe = !!item.my_reservation || !!anonToken`
  - States: Reserve button (not reserved) / cancel + fulfill controls (reserved by me) / "already reserved" label (reserved by someone else)
  - Emits: `reserve`, `cancel`, `fulfill`

- Created `apps/web/components/shared/ReservationModal.vue`:
  - Three states: `registered_only` + unauthenticated → login button; authenticated → confirm; anonymous → name input
  - Emits `reserved(itemId, anonToken | null)` on success

### Pages

- Replaced stub `apps/web/pages/w/[slug].vue`:
  - Uses `useSharedWishlist`, `useReservationStore`, `useReservationsApi`, `useAuthStore`
  - `displayItems` local ref with optimistic updates on reserve/cancel/fulfill
  - `onMounted(() => reservationStore.load())` — loads anon tokens client-side only
  - `useSeoMeta` wired to wishlist title, description, cover_url

### Modified existing files

- `apps/web/pages/wishlists/[id]/index.vue`:
  - Added `onFulfillItem(item)` — calls `reservationsApi.fulfill()`, updates `itemStore.updateOne()`, syncs `detailItem.value`
  - Wired `@fulfill="onFulfillItem"` on both grid and masonry `ItemsItemCard` instances and on `ItemsItemDetailModal`

- `apps/web/components/items/ItemDetailModal.vue`:
  - Added `fulfill` emit declaration
  - Added fulfill toggle button (`v-if="item.is_reserved"`) in the detail view — shows "fulfill" / "unfulfill" based on `item.is_fulfilled`

- `apps/web/components/items/ItemCard.vue`:
  - Added fulfill button in hover overlay, guarded with `v-if="item.is_reserved"` to prevent 404s on unreserved items
  - Label toggles between `t('items.fulfill')` and `t('reservation.unfulfill')`

### i18n

- Added keys to `apps/web/locales/en.json` and `apps/web/locales/uk.json`:
  - `reservation.*` — reserve, confirm, cancel, name prompt, registered-only message, fulfill/unfulfill labels
  - `shared.*` — no_items, already_reserved

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Anonymous token storage | `localStorage` under `wishpicks_reservation_tokens` | Cookies would conflict with HTTP-only auth cookie strategy |
| Token transmission | `X-Anon-Token` request header | Clean separation from auth flow; easy to strip server-side |
| Shared page item visibility | Show all items including `is_surprise` ones | Owner controls visibility at wishlist level, not item level |
| Fulfillment scope | Both shared page (by reserver) and owner dashboard | Owner needs to track what was actually purchased |
| `registered_only` unauthenticated | Redirect to `/login` | Simpler than inline modal; reserver identity required |

---

## Bugs Fixed

1. **`useReservationsApi is not defined` (SSR error)** — Nuxt does not auto-import composables from `composables/api/` subdirectories. Fixed by adding explicit `import` statements in three files: `pages/wishlists/[id]/index.vue`, `components/shared/ReservationModal.vue`, `pages/w/[slug].vue`.

2. **404 on fulfill button for unreserved items** — `ItemCard.vue` showed the "Виконати" button for all items in the hover overlay regardless of reservation state. Fixed by wrapping the button with `v-if="item.is_reserved"`.
