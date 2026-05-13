# URL Parser (API)

## Description

Implemented `POST /api/items/parse-url` — scrapes a product URL and returns prefilled wish item fields (title, description, image, price, currency). Covers HTML fetching, BeautifulSoup extraction, Cloudinary image upload, currency conversion via frankfurter.app, and Redis caching with 1-hour TTL.

---

## Session Log

### Schemas

- Modified `apps/api/app/schemas/items.py`:
  - Added `ParseUrlRequest` — `{ url: str }` with `min_length=1`
  - Added `ParseUrlData` — nullable fields: `title`, `description`, `image_url`, `price` (Decimal), `currency`, plus required `product_url`
  - Added `ParseUrlResponse` — `{ data: ParseUrlData }` envelope

### Service

- Created `apps/api/app/services/url_parser.py`:
  - `RawParsed` dataclass — raw extracted values before enrichment
  - `ParsedItemData` dataclass — enriched values returned to the router
  - `_normalize_url(url)` — lowercase scheme/host, strips trailing slash
  - `_cache_key(url)` — `url_parse:{sha256(normalized_url)}`
  - `_fetch_html(url)` — async httpx stream with browser User-Agent, 10s timeout, 2 MB body cap
  - `_og(soup, prop)` / `_meta_name(soup, name)` — meta tag helpers
  - `_jsonld_price(soup)` — extracts price/currency from `<script type="application/ld+json">` `Product.offers`
  - `_extract_fields(html)` — BeautifulSoup parser; priority: `og:title` → `meta[name=title]` → `<title>`, `og:description` → `meta[name=description]`, `og:image`, `og:price:amount` → JSON-LD, `og:price:currency`
  - `_download_image(url)` — async httpx download with browser UA
  - `_convert_currency(price, from_currency)` — calls `api.frankfurter.app/latest?from=X&to=UAH`; on failure returns original price + currency (graceful degradation)
  - `_enrich(raw, product_url)` — converts unsupported currency → UAH; downloads og:image and uploads to Cloudinary `items/` folder via `media_service.upload_image`; Cloudinary failure → `image_url=None` (graceful degradation)
  - `parse_url(url, redis)` — public entry point: validates scheme, checks Redis cache, orchestrates fetch → extract → enrich, writes result to Redis (TTL=3600s), returns `ParsedItemData`

### Router

- Modified `apps/api/app/routers/items.py`:
  - Added imports: `limiter`, `get_redis`, `ParseUrlData`, `ParseUrlRequest`, `ParseUrlResponse`, `url_parser_service`
  - Added `POST /parse-url` before existing `GET /{item_id}`:
    - Auth required (`get_current_user`)
    - Rate limited: `10/minute` (IP-based, consistent with rest of codebase)
    - Depends on `get_redis` for cache access
    - Does not use `db` — no database queries on this endpoint

### Architecture cleanup

- Modified `.ai/ARCHITECTURE.md`:
  - Removed `POST /api/wishlists/:id/items/from-url` from Wish items API section — not needed given the confirmed UI flow (parse → user edits → manual save)

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Service structure | Layered: `_fetch_html` → `_extract_fields` → `_enrich` | Each step has one responsibility; failure location is immediately obvious |
| Currency support | UAH/USD/EUR/GBP kept as-is; anything else converted to UAH via frankfurter.app | Matches frontend dropdown exactly; frankfurter.app is free, no API key required |
| Currency conversion failure | Return original price + original currency | Better to show unconverted data than to surface an error over a secondary concern |
| Cloudinary failure | Return `image_url: null`, rest of fields intact | Image is supplementary; a Cloudinary outage should not break the whole parse flow |
| Redis unavailability | Skip cache, fall through to live fetch | Graceful degradation; no error raised to caller |
| Cache key | `url_parse:{sha256(normalized_url)}` | Normalized URL prevents duplicate cache entries for equivalent URLs |
| Image sources | Only `og:image` (one image) | Simpler and reliable; multiple-image extraction deferred to future iteration |
| Parser extracts nothing | `200` with all fields `null` | Not an error — user fills manually; matches spec |
| `from-url` endpoint | Removed | UI flow requires user review before save; combined endpoint adds no value |
