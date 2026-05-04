# Wishpicks Web

Nuxt 3 frontend for the Wishpicks wishlist platform.

## Stack

| Concern | Technology |
|---|---|
| Framework | Nuxt 3 |
| UI library | @nuxt/ui v3 (Tailwind-based) |
| State management | Pinia (@pinia/nuxt) |
| i18n | @nuxtjs/i18n v9 |
| Language | TypeScript |
| Linting | ESLint (@nuxt/eslint) |
| Formatting | Prettier + prettier-plugin-tailwindcss |

## Local development

All services run through Docker Compose from the repo root:

```bash
# Start everything (Postgres + Redis + API + Web)
docker-compose up

# Frontend is available at http://localhost:3000
# Nuxt devtools at http://localhost:3000/_nuxt/
```

The web container mounts `./apps/web` as a volume and runs Nuxt with `--host 0.0.0.0`, so file changes trigger HMR immediately without rebuilding.

Or run locally (Node 20+ required):

```bash
cd apps/web
npm install
npm run dev       # http://localhost:3000
```

## Environment variables

Set via `.env` at the repo root. Nuxt reads `NUXT_PUBLIC_*` automatically:

| Variable | Maps to | Description |
|---|---|---|
| `NUXT_PUBLIC_API_BASE_URL` | `runtimeConfig.public.apiBaseUrl` | Backend base URL, e.g. `http://localhost:8000` |
| `NUXT_PUBLIC_CLOUDINARY_CLOUD_NAME` | `runtimeConfig.public.cloudinaryCloudName` | Cloudinary cloud name for image uploads |

Access in code:

```ts
const { public: { apiBaseUrl } } = useRuntimeConfig()
```

## Project structure

```
app.vue                        # Root component — wraps <NuxtPage> in layout
nuxt.config.ts                 # Nuxt config — modules, i18n, runtimeConfig, Vite settings
pages/
├── index.vue                  # Landing page
├── login.vue                  # Email/password login
├── register.vue               # Registration
├── dashboard.vue              # Authenticated home
├── profile.vue                # User profile settings
├── saved.vue                  # Saved wishlists and items
├── wishlists/
│   ├── new.vue                # Create wishlist
│   ├── [id]/index.vue         # Wishlist detail (owner view)
│   └── [id]/settings.vue     # Wishlist settings
├── w/[slug].vue               # Public shared wishlist (guest view)
└── auth/google/callback.vue   # Google OAuth redirect handler
components/
├── ui/
│   └── LanguageSwitcher.vue   # UK / EN toggle
├── auth/                      # Auth form components (to be built)
├── items/                     # Wish item components (to be built)
└── wishlist/                  # Wishlist card / list components (to be built)
composables/
├── useAuth.ts                 # User state composable — wraps store + handles 401 → refresh → retry
└── api/
    └── useAuth.ts             # Raw API calls: register, login, logout, refresh, me
stores/
├── useAuthStore.ts            # Current user + isAuthenticated getter
├── useWishlistStore.ts        # Wishlists CRUD state
├── useItemStore.ts            # Wish items state
└── useSavedStore.ts           # Saved wishlists and items state
locales/
├── uk.json                    # Ukrainian (default locale)
└── en.json                    # English
plugins/
└── i18n-messages.ts           # Registers locale messages at runtime
i18n.config.ts                 # i18n module config
```

## i18n

Ukrainian is the default locale. URLs are unprefixed for Ukrainian (`/dashboard`) and prefixed for English (`/en/dashboard`).

```ts
// In any component
const { t } = useI18n()
// t('auth.login') → reads from locales/uk.json or locales/en.json
```

All user-facing strings **must** go in `locales/uk.json` and `locales/en.json`. No hardcoded text in `.vue` files.

## API calls

**Never call `$fetch` directly from a component.** All API calls go through composables:

```
composables/api/useAuth.ts       → wraps fetch for /api/auth/* endpoints
composables/api/useWishlists.ts  → wraps fetch for /api/wishlists/* (to be built)
composables/api/useItems.ts      → wraps fetch for /api/items/* (to be built)
```

The composable layer owns error parsing, response unwrapping, and the 401 → token refresh → retry flow. Stores consume composables; components consume stores.

Auth cookies are HTTP-only and managed by the browser — no token handling in frontend JS.

## State management rules

- One Pinia store per domain: `useAuthStore`, `useWishlistStore`, `useItemStore`, `useSavedStore`
- `useAuth` composable is the only place that reads/writes `useAuthStore`
- Components call composable methods, not store actions directly

## Linting and formatting

```bash
# Inside the web container
docker exec wishpicks-web-1 npm run lint
docker exec wishpicks-web-1 npm run lint:fix
docker exec wishpicks-web-1 npm run format

# Or locally
cd apps/web
npm run lint
npm run lint:fix
npm run format
```

ESLint config: `eslint.config.mjs` (flat config, @nuxt/eslint + eslint-config-prettier)
Prettier config: `.prettierrc`

## Building for production

```bash
docker-compose up -d --build web
```

Required when `package.json` dependencies change. For code-only changes the volume mount handles it.

```bash
# Standalone production build (outside Docker)
cd apps/web
npm run build
npm run preview   # serves the built output locally
```

## Auth flow notes

- Tokens live in HTTP-only cookies set by the API — the frontend never reads or stores them
- On 401 responses the `useAuth` composable should attempt one silent token refresh (`POST /api/auth/refresh`), then retry the original request
- If the refresh also fails the user is considered logged out — clear store state and redirect to `/login`
- The `optional_current_user` pattern on shared wishlist pages (`/w/[slug]`) means the API returns public data whether or not the user is authenticated; the frontend should pass cookies regardless so the API can personalize the response when a session exists
