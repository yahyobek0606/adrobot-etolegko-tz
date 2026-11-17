# Keitaro Campaign Manager

Create Keitaro campaigns (geo → Google, everyone else → offer) and manage offer shares in existing ones.
FastAPI + SQLAlchemy + PostgreSQL, React + TypeScript, Docker Compose.

## Setup

Requires Docker with Compose v2.

```bash
cp .env.example .env
```

Set `KEITARO_API_KEY` in `.env`. Everything else has working defaults.

## Run

```bash
docker compose up --build
```

- App: http://localhost:5173
- API docs: http://localhost:8000/docs

Migrations run automatically when the backend starts.

## Migrations

```bash
docker compose exec backend uv run alembic upgrade head                      # apply
docker compose exec backend uv run alembic downgrade -1                      # roll back one
docker compose exec backend uv run alembic revision --autogenerate -m "msg"  # create
```

## Tests

```bash
docker compose exec backend uv run pytest
docker compose exec frontend pnpm test
```

## More

- Assignment: [requirements/tz.md](requirements/tz.md)
- Product decisions: [requirements/PRODUCT.md](requirements/PRODUCT.md)
- Keitaro API notes: [docs/keitaro-api.md](docs/keitaro-api.md)
