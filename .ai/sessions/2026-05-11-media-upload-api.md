# Media Upload (API)

## Description

Implemented the generic image upload endpoint via Cloudinary. Covers file validation (type, size, folder), server-side upload with async wrapping, and a `POST /api/media/upload` route. Also hardened `avatar_url` on the user update schema with proper HTTP URL validation.

---

## Session Log

### Dependency

- Modified `apps/api/pyproject.toml`:
  - Added `python-multipart>=0.0.12` — required by FastAPI to parse `multipart/form-data` (used by `UploadFile`)
  - Installed live in the running container via `uv pip install --system python-multipart` (next `docker-compose build` will pick it up automatically from `pyproject.toml`)

### Cloudinary configuration

- Modified `apps/api/app/main.py`:
  - Added `import cloudinary` and a `cloudinary.config(...)` call at module level, before `app = FastAPI(...)`, reading `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET` from `settings`
  - `secure=True` ensures all returned URLs use HTTPS

### Schemas

- Replaced stub `apps/api/app/schemas/media.py`:
  - `MediaUploadData` — `{ url: str }`
  - `MediaUploadResponse` — `{ data: MediaUploadData }` — consistent envelope shape with the rest of the project

### Service

- Replaced stub `apps/api/app/services/media.py`:
  - `upload_image(file_bytes, content_type, folder) -> str`
  - Validates `content_type` against `{"image/jpeg", "image/png", "image/webp"}` → `400 INVALID_FILE_TYPE`
  - Validates `len(file_bytes) <= 5 MB` → `400 FILE_TOO_LARGE`
  - Validates `folder` is one of `{"avatars", "covers", "items", "general"}` → `400 INVALID_FOLDER`
  - Calls `cloudinary.uploader.upload()` wrapped in `asyncio.to_thread()` to avoid blocking the async event loop
  - Uploads to `wishpicks/{folder}/` in the Cloudinary account
  - Returns `result["secure_url"]`
  - On any Cloudinary exception → `422 UPLOAD_FAILED`

### Router

- Replaced stub `apps/api/app/routers/media.py`:
  - `POST /upload` — auth required (`get_current_user`), rate-limited 20/minute
  - Form fields: `file: UploadFile`, `folder: str = "general"`
  - Reads all bytes, calls `media_service.upload_image`, returns `MediaUploadResponse`
  - Router was already registered in `main.py` at prefix `/api/media`

### Users schema hardening

- Modified `apps/api/app/schemas/users.py`:
  - Added `_url_adapter = TypeAdapter(AnyHttpUrl)` module-level constant
  - Added `avatar_url_is_http` field validator on `UserUpdateRequest.avatar_url` — validates input as a proper HTTP/HTTPS URL via `_url_adapter.validate_python(v)`, returns the original `str` value (no type change, safe for SQLAlchemy)

---

## Key Design Decisions

| Decision | Choice | Reason |
|---|---|---|
| Generic vs avatar-specific endpoint | Generic with `folder` hint | Reusable for wishlist covers and item images without any future changes |
| Allowed folders | `avatars`, `covers`, `items`, `general` | Maps to clear Cloudinary folder structure under `wishpicks/` |
| Cloudinary call wrapping | `asyncio.to_thread()` | Cloudinary SDK is synchronous; wrapping avoids blocking the async event loop |
| Upload decoupled from entity update | Two separate requests | Keeps upload generic and entity schemas clean; no coupling between media and user/wishlist models |
| `avatar_url` validation | `TypeAdapter(AnyHttpUrl)` + return `str` | Validates format without changing the field type, safe for SQLAlchemy `String` column |
