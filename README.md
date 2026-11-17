# Keitaro Campaign Manager

A web app on top of the [Keitaro](https://keitaro.io) ad tracker:

- **Campaign creator**: creates a campaign with two streams. The first sends visitors from the chosen countries to Google, the second sends everyone else to the selected offer. Domain, group and traffic source are set on creation.
- **Campaign editor**: add, archive and restore offers in a campaign, pin shares, then push changes to Keitaro or sync from it.

Requirements: [requirements/tz.md](requirements/tz.md) (original assignment), [requirements/PRODUCT.md](requirements/PRODUCT.md) (user stories and decisions).

## Stack
- Backend: FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL 16
- Frontend: React, TypeScript, Vite, shadcn/ui, TanStack Query
- Infrastructure: Docker Compose

## Requirements
- Docker with Docker Compose v2
- Optional, for running tooling outside Docker: `uv`, Node 22+ and pnpm
- A Keitaro instance and an Admin API key

## Setup
```bash
git clone <repo-url>
cd adrobot-etolegko-tz
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `KEITARO_BASE_URL` | Keitaro instance URL |
| `KEITARO_API_KEY` | Keitaro Admin API key |
| `KEITARO_DOCS_URL`, `KEITARO_DOCS_LOGIN`, `KEITARO_DOCS_PASSWORD` | Keitaro admin login, only needed to read the API docs. Not used by the app |
| `KEITARO_DEFAULT_DOMAIN_ID` | Domain preselected in the creator form |
| `KEITARO_DEFAULT_GROUP_ID` | Campaign group preselected in the creator form |
| `KEITARO_DEFAULT_TRAFFIC_SOURCE_ID` | Traffic source preselected in the creator form |

The Keitaro endpoints this app uses are documented in [docs/keitaro-api.md](docs/keitaro-api.md).
| `FALLBACK_REDIRECT_URL` | Where the geo stream redirects, default `https://google.com` |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Local database credentials |
| `DATABASE_URL` | SQLAlchemy URL built from the values above |
| `CORS_ORIGINS` | Allowed frontend origins |

## Run
```bash
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000/api/v1 |
| API docs (Swagger) | http://localhost:8000/docs |

Migrations are applied automatically when the backend container starts.

## Migrations
```bash
docker compose exec backend uv run alembic upgrade head
docker compose exec backend uv run alembic revision --autogenerate -m "describe change"
docker compose exec backend uv run alembic downgrade -1
```

## Tests and checks
```bash
docker compose exec backend uv run pytest
docker compose exec backend uv run ruff check .
docker compose exec backend uv run mypy app

docker compose exec frontend pnpm test
docker compose exec frontend pnpm typecheck
docker compose exec frontend pnpm lint
```

## Regenerate frontend API types
After changing backend schemas:
```bash
docker compose exec -e API_URL=http://backend:8000 frontend pnpm gen:api
```

## Project structure
```
backend/       FastAPI app, Alembic migrations, tests
frontend/      React app
requirements/  assignment and product spec
compose.yaml   local stack
```
