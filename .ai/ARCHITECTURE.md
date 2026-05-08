# Wishpicks — MVP Specification

> This document describes architecture, data flow, and technical decisions.

---

## 1. Product

**Wishpicks** is a wishlist platform. A user creates a gift wishlist, shares a link with friends. Friends can reserve items to prevent duplicate gifts. The wishlist owner **never sees who reserved what** — the surprise is preserved by design.

### Core user scenarios

1. Register → create a wishlist → add items → share link
2. Guest opens a shared link (no auth required) → views list → reserves an item
3. Authenticated user saves someone else's wishlist or a specific item to their collection
4. User pastes a product URL → app automatically pulls title, image, price, and description

---

## 2. Monorepo Structure

```
wishpicks/
├── apps/
│   ├── web/          # Nuxt 3 — frontend
│   └── api/          # FastAPI — backend
├── docker-compose.yml
├── .env.example
└── README.md
```

- Root `package.json` with workspaces handles JS tooling
- Python managed via `pyproject.toml` inside `apps/api`
- Shared `.env.example` documents every required environment variable
- Local development runs entirely via `docker-compose` (Postgres + API + Web)

---

## 3. Tech Stack

### Frontend — `apps/web`

| Concern | Decision | Reason |
|---|---|---|
| Framework | Nuxt 3 | SSR required for OG meta tags on shared wishlist pages |
| State management | Pinia | SSR-safe, official Vue recommendation |
| Styling | Tailwind CSS v4 + Nuxt UI | Popular headless UI library, easy to implement. Focus on smooth animations and UX experience |
| Internationalization | `@nuxtjs/i18n` | Ukrainian (default) + English |
| Auth client | Custom composable | HTTP-only cookie flow; no third-party SDK needed |
| Form validation | VeeValidate + Zod | Client-side schemas that mirror backend validation |
| HTTP layer | Native `$fetch` / `useFetch` | Built into Nuxt, no extra dependencies |
| Theme | Nuxt UI Theme component | Simple way to implement theme toggle |

### Backend — `apps/api`

| Concern | Decision | Reason |
|---|---|---|
| Framework | FastAPI | Async, automatic OpenAPI docs, Pydantic-native |
| ORM | SQLAlchemy 2.x (async) | Mature, async support, works well with Alembic |
| DB driver | asyncpg | Required for async SQLAlchemy with Postgres |
| Migrations | Alembic | Version-controlled schema changes |
| Validation | Pydantic v2 | Request/response schemas, settings management |
| Auth | Custom JWT (`python-jose`) | Zero cost, full control, no vendor lock-in |
| Password hashing | `bcrypt` (direct) | passlib incompatible with bcrypt >= 4.0; use bcrypt library directly |
| URL scraping | `httpx` + `BeautifulSoup4` | Async HTTP + HTML parsing for product import |
| Rate limiting | slowapi + Redis (Upstash) | Persistent rate limit counters across restarts and multiple workers |
| Cache | Redis (Upstash) | URL parser cache, session blocklist; free serverless tier via HTTP |
| Settings | `pydantic-settings` | Typed config from `.env` file |

### Infrastructure

| Concern | Decision | Notes |
|---|---|---|
| Database | Neon | Free tier serverless Postgres |
| Media storage | Cloudinary | Free tier, 25 GB, handles image transforms |
| Frontend hosting | Vercel | Free tier, native Nuxt SSR support |
| Backend hosting | Railway or Render | Free tier sufficient for MVP traffic |
| CI | Github Actions | Releases, CI builds |
| Cache / Rate limit store | Upstash Redis | Free tier: 10k commands/day, 256 MB; HTTP-based, no sidecar needed |
| Local dev | Docker Compose | Postgres + Redis + API + Web, fully reproducible |

> **Rule:** Every infrastructure choice must have a free tier covering ~1,000 users. 

---

## 4. Authentication & Security

Authentication is the highest-priority system. Implement it correctly from day one — no shortcuts.

### 4.1 Strategy

**JWT with HTTP-only cookies.** Tokens are never stored in `localStorage` and never returned in response bodies accessible to JavaScript.

- `access_token` — short-lived (15 minutes), sent on every authenticated request via cookie
- `refresh_token` — long-lived (30 days), scoped to the `/api/auth/refresh` path only
- Both cookies set with: `HttpOnly`, `Secure` (production only), `SameSite=Lax`

### 4.2 Token lifecycle

```
Register / Login
  → server issues access_token + refresh_token via Set-Cookie headers
  → response body returns only { user } — no token values in body

Every authenticated request
  → browser sends access_token cookie automatically
  → server validates signature + expiry on each request

Access token expires
  → frontend detects 401 response
  → frontend calls POST /api/auth/refresh silently
  → server rotates both tokens (new pair issued, old refresh token revoked in DB)
  → original request is retried transparently

Logout
  → server revokes refresh token in DB
  → server clears both cookies (Max-Age=0)
```

### 4.3 Refresh token rotation & theft detection

- Every refresh token has a unique `jti` (JWT ID) stored in the database with a `revoked` flag
- On refresh: validate `jti` exists + not revoked + not expired → issue new pair → mark old `jti` as revoked
- If a **revoked** `jti` is presented → **immediately revoke ALL tokens for that user** and return 401
- This detects replay attacks where a stolen token is used after the legitimate user already refreshed

Revoked JTIs are additionally stored in Redis with TTL matching the token's remaining lifetime — this allows fast rejection at middleware level without a DB query on every request.

### 4.4 Google OAuth

Google OAuth is an additional login method, not a hard dependency. Flow:

1. User clicks "Continue with Google" → frontend redirects to `GET /api/auth/google`
2. Backend redirects user to Google's OAuth consent screen
3. Google redirects to `GET /api/auth/google/callback` (public endpoint)
4. Backend exchanges the code for a Google profile → upserts user record → issues JWT cookies → redirects to frontend
5. If a user with the same email already exists (email/password account), `google_id` is linked to that existing account automatically

### 4.5 Password rules

- Minimum 8 characters, validated server-side by Pydantic before hashing
- Hashed with bcrypt, cost factor 12
- Never logged, never returned in any API response

### 4.6 Rate limiting

Applied via slowapi backed by Redis (Upstash in production, local Redis container in dev). Redis ensures rate limit counters persist across 
API restarts and work correctly if multiple backend workers are running.

| Endpoint | Limit |
|---|---|
| `POST /api/auth/login` | 5 / minute / IP |
| `POST /api/auth/register` | 3 / minute / IP |
| `POST /api/items/parse-url` | 10 / minute / authenticated user |
| All other auth endpoints | 10 / minute / IP |

### 4.7 General security rules

- All IDs exposed in the API are **UUID v4** — never auto-increment integers
- All request bodies validated by Pydantic; raw user input is never trusted
- No user-supplied HTML stored or rendered at MVP — plain text only
- CORS: whitelist only the frontend origin via env var; never `*` in production
- Security headers on every response: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`
- CSRF mitigation: validate `Origin` / `Referer` headers on all state-mutating requests via FastAPI middleware

---

## 5. Data Model

### Entity relationships

```
User ──< Wishlist ──< WishItem ──── Reservation
                               └──< SavedItem >──< User
         └─────────────────────────< SavedWishlist >──< User
User ──< RefreshToken
```

### Users

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `email` | text, unique | |
| `username` | text, unique, nullable | Optional; used in public profile URL |
| `display_name` | text, nullable | |
| `avatar_url` | text, nullable | Cloudinary URL |
| `password_hash` | text, nullable | Null for Google-only accounts |
| `google_id` | text, unique, nullable | |
| `is_active` | boolean | Default true |
| `created_at` / `updated_at` | timestamptz | |

### Wishlists

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `user_id` | FK → users | Cascade delete |
| `title` | text | |
| `description` | text, nullable | |
| `cover_url` | text, nullable | Cloudinary URL |
| `event_type` | enum, nullable | `birthday`, `wedding`, `new_year`, `other` |
| `is_public` | boolean | `false` = link-only (not discoverable) |
| `slug` | text, unique | Short random string; used in share URL; generated server-side |
| `created_at` / `updated_at` | timestamptz | |

### Wish items

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `wishlist_id` | FK → wishlists | Cascade delete |
| `title` | text | |
| `description` | text, nullable | |
| `image_url` | text, nullable | |
| `price` | decimal(12,2), nullable | |
| `currency` | char(3) | ISO 4217, default `UAH` |
| `product_url` | text, nullable | Link to original product page |
| `priority` | smallint | `0` = normal, `1` = high, `2` = must-have |
| `is_surprise` | boolean | If true, hidden from owner on shared view |
| `position` | integer | Manual sort order within wishlist |
| `created_at` / `updated_at` | timestamptz | |

### Reservations

| Field | Type | Notes |
|---|---|---|
| `id` | UUID PK | |
| `item_id` | FK → wish_items, **unique** | One reservation per item, enforced by DB constraint |
| `reserver_id` | FK → users, nullable | Null for anonymous reservers |
| `reserver_name` | text, nullable | Display name for anonymous |
| `created_at` | timestamptz | |

**Critical:** The API must **never return `reserver_id` or `reserver_name`** to the wishlist owner. Only `is_reserved: boolean` is exposed. This rule is enforced at the serialization layer, not in the frontend.

### Saved wishlists & items

`saved_wishlists`: composite PK (`user_id`, `wishlist_id`), `saved_at`

`saved_items`: composite PK (`user_id`, `item_id`), `saved_at`

### Refresh tokens

| Field | Type | Notes |
|---|---|---|
| `jti` | UUID PK | JWT ID |
| `user_id` | FK → users | Cascade delete |
| `expires_at` | timestamptz | |
| `revoked` | boolean | Default false |
| `created_at` | timestamptz | |

---

## 6. API Structure

All endpoints prefixed with `/api`. Auth required unless marked `[public]`.

### Auth

```
POST   /api/auth/register
POST   /api/auth/login
POST   /api/auth/logout
POST   /api/auth/refresh
GET    /api/auth/me
GET    /api/auth/google
GET    /api/auth/google/callback     [public]
```

### Users

```
GET    /api/users/me
PATCH  /api/users/me
DELETE /api/users/me
```

### Wishlists

```
GET    /api/wishlists                # owner's wishlists list
POST   /api/wishlists
GET    /api/wishlists/:id            # full owner view (reserver identity hidden)
PATCH  /api/wishlists/:id
DELETE /api/wishlists/:id

GET    /api/w/:slug                  [public] shared guest view
```

### Wish items

```
GET    /api/wishlists/:id/items
POST   /api/wishlists/:id/items           # manual add
PATCH  /api/items/:id
DELETE /api/items/:id
PATCH  /api/items/:id/position            # update sort order

POST   /api/items/parse-url               # { url } → scraped fields preview
POST   /api/wishlists/:id/items/from-url  # parse + create in one step
```

### Reservations

```
POST   /api/items/:id/reserve        [public*]
DELETE /api/items/:id/reserve        [public*]
```

`[public*]` = no auth required, rate-limited per IP. If authenticated, `reserver_id` is stored on the reservation record.

### Saved

```
GET    /api/saved/wishlists
POST   /api/saved/wishlists/:id
DELETE /api/saved/wishlists/:id

GET    /api/saved/items
POST   /api/saved/items/:id
DELETE /api/saved/items/:id
```

---

## 7. URL Parser (Product Import)

**Purpose:** User pastes a product link → API returns prefilled item fields → user reviews and saves.

### Flow

1. Client sends `POST /api/items/parse-url` with `{ url }`
2. Backend validates: URL scheme must be `http` or `https`
3. Backend fetches the page with a browser-like User-Agent, 10s timeout, 2 MB max body
4. Parser extracts fields in this priority order:

| Field | Priority order |
|---|---|
| Title | `og:title` → `<meta name="title">` → `<title>` tag |
| Description | `og:description` → `<meta name="description">` |
| Image | `og:image` |
| Price | `og:price:amount` → JSON-LD `Product.offers.price` → null |
| Currency | `og:price:currency` → fallback `UAH` |

5. Response returns extracted fields; client prefills the add-item form
6. **Parser output is never saved directly** — user must confirm / edit before saving
7. If parsed response failed - user should manually enter corresponding fields.

### Caching

- Parsed URLs cached in Redis with 1-hour TTL, keyed by normalized URL
- Same URL within TTL returns cached result without re-fetching
- Redis cache survives API restarts and is shared across workers
- On cache miss: fetch + parse + store result; on Upstash connection failure: fall through to live fetch (graceful degradation)

### Error handling

- Invalid URL scheme → 400
- Fetch fails (timeout, 4xx, 5xx, non-HTML content type) → 422 with descriptive message
- Parser extracts nothing → 200 with all fields null (user fills manually)

---

## 8. Media Upload

**Service:** Cloudinary free tier.

### Flow

1. Client selects an image file
2. Client sends file to `POST /api/media/upload`
3. Backend validates: accepted types are JPEG, PNG, WebP; max size 5 MB
4. Backend uploads to Cloudinary via server-side API (Cloudinary credentials never exposed to the client)
5. Cloudinary returns a permanent secure URL
6. Backend returns `{ url }` to the client
7. Client uses this URL in the item's `image_url` field when saving the item

### Rules

- Upload is always server-side — no direct unsigned client-to-Cloudinary uploads
- No image processing pipeline at MVP — use Cloudinary URL transform parameters in the frontend for resizing
- Orphaned uploads (file uploaded but item never saved) are acceptable at MVP scale

---

## 9. Frontend Structure

### Pages

```
/                              Landing page (public)
/login                         Login form
/register                      Registration form
/auth/google/callback          OAuth redirect handler (no UI, just processes tokens)

/dashboard                     User's wishlists overview
/wishlists/new                 Create wishlist form
/wishlists/:id                 Edit wishlist + manage items
/wishlists/:id/settings        Wishlist settings (privacy, event, cover image)

/w/:slug                       Public shared wishlist — guest view (SSR)

/profile                       User profile settings
/saved                         Saved wishlists and items tabs
```

### Shared wishlist page `/w/:slug`

- Rendered **server-side** so OG meta tags populate correctly when the URL is pasted in messengers or social media
- OG tags populated from wishlist `title`, `description`, `cover_url`
- No authentication required to view or reserve
- Anonymous reservation: guest provides their name
- If user is logged in, reservation is attributed to their account
- `is_surprise` items are filtered out server-side before the response is sent

### Auth composable

- Wraps all auth-related API calls in one reusable composable
- Manages `user` state in a Pinia store
- On app init: calls `GET /api/auth/me` to restore session from existing cookie
- On any 401 response: attempts one silent refresh via `POST /api/auth/refresh`, then retries the original request
- If refresh fails: clears user state, redirects to `/login`
- All other parts of the app interact with auth only through this composable

### i18n

- Default locale: `uk` (Ukrainian)
- Secondary locale: `en` (English)
- Language switcher in global header
- All user-facing strings in locale translation files — no hardcoded UI text anywhere
- Locale preference stored in a cookie (SSR-compatible, unlike `localStorage`)

### Theme

- Dark / Light toggle in global header
- Preference stored in `localStorage`
- On first visit: system preference (`prefers-color-scheme`) applied if no saved preference
- Implemented via Tailwind `dark:` variant and CSS custom properties

### Nuxt UI
- Read the LLM documentation for Nuxt UI if needed or you have doubts (https://ui.nuxt.com/llms.txt)

### SEO

Every page has a defined meta strategy. Implemented via Nuxt's built-in useHead / useSeoMeta composables — no third-party SEO library needed.

| Page | Title | Description | OG Image |
|---|---|---|---|
| `/` | Wishpicks — Create & Share Wishlists | Static | Static brand image |
| `/w/:slug` | `{wishlist.title}` — Wishpicks | `{wishlist.description}` (truncated to 160 chars) | `wishlist.cover_url` or fallback brand image |
| `/dashboard` | My Wishlists — Wishpicks | Static | None |
| All auth pages | Login / Register — Wishpicks | Static | None |
| `/` | Wishpicks — Create & Share Wishlists | Static | Static brand image |

Rules:

- /w/:slug is the only page that matters for social sharing — it must be SSR-rendered with fully populated OG tags before the HTML reaches the client. Verify with Facebook Debugger / Telegram link preview.
- og:url always uses the canonical absolute URL including domain (from env var NUXT_PUBLIC_APP_URL)
- og:type is website on all pages
- twitter:card is summary_large_image on /w/:slug, summary on all others
- Wishlist pages with is_public: false get <meta name="robots" content="noindex, nofollow"> — prevents indexing of link-only wishlists
- Public wishlists (is_public: true) are indexable; include a canonical tag
- sitemap.xml is generated at build time (static routes) + runtime (public wishlist slugs via API call during generation)
- robots.txt disallows /dashboard, /profile, /saved, /auth

### Structured Data (JSON-LD)

Add JSON-LD on the shared wishlist page `(/w/:slug)` to improve link previews and search appearance:

- Type: ItemList containing each wish item as a ListItem with name, url, image
- Injected via useHead as a <script type="application/ld+json"> tag server-side
- Only rendered on SSR — do not add on client-only pages

---

## 10. Business Rules

These rules are enforced at the **API level**. The frontend may reflect them in UI, but they must not rely on the frontend for enforcement.

| Rule | Where enforced |
|---|---|
| Owner never sees who reserved their item | API serializer strips reserver identity from owner-facing responses |
| Only the wishlist owner can add / edit / delete items | Ownership check on every mutating item endpoint |
| Only the reserver can cancel their reservation | `reserver_id` match for authenticated users; session-token for anonymous (MVP: just allow by IP/name match) |
| `is_surprise` items hidden from owner on shared view | Server-side filter on `GET /api/w/:slug` |
| One reservation per item | `UNIQUE` constraint on `item_id` in the reservations table |
| Slugs are randomly generated, never user-defined | Generated server-side on wishlist creation |
| `is_public: false` wishlists are not discoverable | No search or listing endpoint exposes private wishlists; only direct slug access works |
| Wishlists and items belong to one user | Foreign key + ownership check on every operation |

---

## 11. Development Phases

Phases represent logical groupings of work, completed in order. No dates attached.

### Phase 1 — Foundation

- Monorepo setup, Docker Compose configuration, environment variable structure
- Database schema design + initial Alembic migration
- Nuxt project setup: routing, i18n configuration, dark/light theme, auth composable + Pinia store
- Full auth system: register, login, logout, token refresh, refresh token rotation + theft detection
- Google OAuth integration
- User profile read + update

### Phase 2 — Core product

- Wishlist CRUD (create, read, update, delete)
- Wish item CRUD — manual form entry
- URL parser endpoint + frontend integration (paste URL → prefill form)
- Image upload via Cloudinary
- Public shared wishlist page (`/w/:slug`) with SSR and OG meta tags
- Reservation flow — authenticated and anonymous

### Phase 3 — Social + polish

- Save wishlist / save item (bookmark feature)
- Saved items and wishlists page
- Manual item sort order (drag to reorder)
- Mobile-responsive UI pass across all pages
- Loading skeletons, error states, empty states
- Web Share API for native share sheet on mobile
- Basic SEO: sitemap, robots.txt, canonical tags

### Phase 4 — Post-MVP (do not implement now)

- Partner / shop integrations with affiliate links
- Discover feed page with partner products
- Admin panel for partner management
- Analytics and conversion tracking
- Push or email notifications

---

## 12. Environment Variables

All secrets and configuration managed via `.env` files. Never hardcode any value.

### Backend (`apps/api/.env`)

| Variable | Description |
|---|---|
| `DATABASE_URL` | Neon Postgres connection string |
| `SECRET_KEY` | JWT signing secret — minimum 32 random characters |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Default: 15 |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Default: 30 |
| `GOOGLE_CLIENT_ID` | Google OAuth app client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth app client secret |
| `GOOGLE_REDIRECT_URI` | Must match exactly what's registered in Google Console |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary account cloud name |
| `CLOUDINARY_API_KEY` | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret |
| `FRONTEND_URL` | Frontend origin for CORS and OAuth redirect |
| `ENVIRONMENT` | `development` or `production` |
| `REDIS_URL` | Upstash Redis connection string (rediss://...) |

### Frontend (`apps/web/.env`)

| Variable | Description |
|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | Backend base URL |
| `NUXT_PUBLIC_CLOUDINARY_CLOUD_NAME` | For frontend image URL construction only |

---

## 13. Non-functional Requirements

### Security

- All tokens in HTTP-only cookies — never in `localStorage` or JS-accessible memory
- Refresh token rotation with theft detection (revoke all sessions on suspicious replay)
- Rate limiting on auth and scraper endpoints
- UUID v4 for all public-facing IDs
- Pydantic validation on every request body
- CORS restricted to the known frontend origin
- Security headers on every response

### Performance

- SSR on shared wishlist pages — required for social sharing previews to work
- Lazy-load images in item lists
- Pagination on wishlists and item lists — cursor-based preferred, offset acceptable at MVP
- URL parser responses cached in Redis (1-hour TTL, shared across workers)
- No N+1 queries — use eager loading for related data in SQLAlchemy

### Reliability

- All schema changes via Alembic migrations — no manual SQL in production
- `.env.example` kept in sync with every new variable added
- `docker-compose up` must bring up a fully working local environment from scratch with a single command
- Production errors must return structured JSON error responses, never raw Python tracebacks

### Accessibility & UX

- Mobile-first responsive layout across all pages
- Skeleton loaders on async data fetches
- Meaningful, user-facing error messages from the API
- Web Share API used for native share on mobile browsers

## 14. API Documentation (Swagger / OpenAPI)

FastAPI generates OpenAPI docs automatically. The following rules ensure the generated docs are useful and accurate — not just auto-generated noise.

Swagger UI and ReDoc are disabled in production (ENVIRONMENT=production). OpenAPI JSON schema (/openapi.json) is also disabled in production.

Required on every endpoint

- `summary` — one short sentence, verb first: "Reserve a wish item", "List current user's wishlists"
- `tags` — one tag per router domain: `auth`, `users`, `wishlists`, `items`, `reservations`, `saved`, `media`
- `response_model` — always explicit; never return raw ORM objects
- `responses` — document non-200 status codes for every endpoint:

Required on every Pydantic schema used in docs

- `model_config = ConfigDict(json_schema_extra={"example": { ... }})` — provide a realistic example object, not placeholder strings like "string" or 0
- Field-level `description` on any non-obvious field: `priority`, `is_surprise`, `slug`, `event_type`