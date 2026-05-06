# Wishpicks

A wishlist platform. Users create gift wishlists and share links with friends. Friends can reserve items to avoid duplicate gifts — the wishlist owner never sees who reserved what.

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Nuxt 3, Pinia, Tailwind CSS v4, Nuxt UI |
| Backend | FastAPI, SQLAlchemy 2 (async), Alembic, Pydantic v2 |
| Database | PostgreSQL (Neon in production) |
| Cache / Rate limiting | Redis (Upstash in production) |
| Media | Cloudinary |
| Frontend hosting | Vercel |
| Backend hosting | Railway / Render |

## Project structure

```
wishpicks/
├── apps/
│   ├── web/          # Nuxt 3 frontend
│   └── api/          # FastAPI backend
├── .github/
│   ├── workflows/    # CI/CD (see below)
│   └── cliff.toml    # Changelog format config
├── .ai/              # Architecture docs, conventions
├── docker-compose.yml
└── .env.example
```

## Getting started

**Prerequisites:** Docker, Docker Compose

```bash
# 1. Copy env file and fill in the required values
cp .env.example .env

# 2. Start all services (Postgres, Redis, API, Web)
docker-compose up
```

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend | http://localhost:8000 |
| API docs | http://localhost:8000/docs |

## Environment variables

All variables are documented in `.env.example`. Required before first run:

Variables without values in `.env.example` are optional for local development (the features that depend on them won't work, but the app will start).

## Commit convention

This project uses [Conventional Commits](https://www.conventionalcommits.org). The format is enforced locally via Husky and in CI via the commitlint workflow.

```
<type>(<scope>): <subject>

feat(api): add reservation endpoint
fix(web): correct auth redirect on 401
chore: update dependencies
feat!: rename endpoint  ← breaking change (! suffix)
```

Allowed types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `style`, `perf`, `ci`, `build`, `revert`

Scope is optional and must be kebab-case when provided.

## CI/CD

### Workflows

**`ci.yml`** — runs on every PR to `main`

Runs two parallel jobs: `Lint API` (ruff check + format check) and `Lint Web` (eslint + nuxt typecheck). Both jobs always run regardless of which files changed.

**`commitlint.yml`** — runs on every PR to `main`

Validates that every commit title in the PR follows the Conventional Commits format. Fails the PR if any commit message is invalid.

**`release.yml`** — runs when a `v*.*.*` tag is pushed

Generates a changelog from commits since the previous tag using [git-cliff](https://github.com/orhun/git-cliff), then creates a GitHub Release with that changelog as the release notes.

### Creating a release

Decide the version bump based on what changed:

| Change type | Bump | Example |
|-------------|------|---------|
| Bug fixes only | patch | `v1.0.0` → `v1.0.1` |
| New features, backward compatible | minor | `v1.0.0` → `v1.1.0` |
| Breaking changes | major | `v1.0.0` → `v2.0.0` |

Then push a tag:

```bash
git tag v1.1.0 -m "Release v1.1.0"
git push origin v1.1.0
```

GitHub Actions picks up the tag, generates the changelog automatically, and publishes the release. No manual steps needed beyond pushing the tag.
