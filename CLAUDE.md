# Keitaro Campaign Manager

A wrapper over the Keitaro ad tracker: create campaigns and manage offer shares in existing campaigns.
Original assignment: `requirements/tz.md`. Product spec: `requirements/PRODUCT.md` (source of truth for behaviour). UI references: `requirements/*.png`.

## Deliverable
- A public GitHub repo with a clear `README.md` covering setup, migrations and launch
- Keep `README.md` in sync whenever setup steps, env vars, commands or services change

## Principles
- clean code
- clean architecture
- extensible and future in mind
- do not write comments until its critically necessary
- Keitaro is one implementation of a generic tracker provider; business logic must never import Keitaro code directly
- No new dependency without a reason; prefer what is listed below

## Infrastructure
- Docker + docker compose, `compose.yaml` at repo root
- Services:
  - `db`: `postgres:16-alpine` with a `pg_isready` healthcheck and a named volume
  - `backend`: `python:3.12-slim` + `uv`, waits for `db` healthy, runs `alembic upgrade head` then `uvicorn --reload`
  - `frontend`: `node:22-alpine` + pnpm (corepack), Vite dev server, proxies `/api` to `backend`
- Source is bind-mounted for hot reload in dev
- Dockerfiles are multi-stage; the production frontend stage builds static files served by `nginx:alpine`
- All config comes from env vars (`.env`, template in `.env.example`). Never commit `.env`

## Backend (`backend/`)

### Packages
| Purpose | Package |
|---|---|
| Web framework | `fastapi`, `uvicorn[standard]` |
| Validation / settings | `pydantic` v2, `pydantic-settings` |
| ORM | `sqlalchemy[asyncio]` 2.0, `asyncpg` |
| Migrations | `alembic` |
| HTTP client | `httpx` |
| Retries | `tenacity` |
| Logging | `structlog` |
| Tests | `pytest`, `pytest-asyncio`, `respx` (mock httpx), `polyfactory` |
| Quality | `ruff` (lint + format), `mypy --strict` |

Python 3.12, dependencies managed by `uv` (`pyproject.toml` + `uv.lock`).

### Layout
```
backend/app/
  main.py         # create_app() factory + lifespan
  api/v1/         # routers + request/response schemas, no business logic
  domain/         # entities, value objects, pure logic (share calculation), domain errors; no I/O
  services/       # use cases orchestrating repositories and providers
  repositories/   # SQLAlchemy data access
  providers/
    base.py       # TrackerProvider Protocol + provider DTOs
    keitaro/      # Keitaro Admin API client + mapping to provider DTOs
  db/             # engine, session factory, ORM models, unit of work
  core/           # settings, logging, dependency wiring, exception handlers
backend/migrations/  # alembic
backend/tests/       # unit/ (domain, services) and integration/ (api, repositories)
```
Dependency direction: `api -> services -> (domain, repositories, providers)`. `domain` imports nothing from the app.

### Patterns
- **App factory** `create_app()` with a `lifespan` that creates and closes the shared `httpx.AsyncClient` and DB engine
- **Async everywhere**: async routes, `AsyncSession`, `httpx.AsyncClient`
- **Dependency injection** via FastAPI `Depends` with `Annotated` aliases (`SessionDep`, `ProviderDep`, `CampaignServiceDep`); wiring lives in `core/dependencies.py`
- **Settings**: one `Settings(BaseSettings)` class, read through a cached `get_settings()`
- **Unit of Work**: one transaction per use case; services call `uow.commit()`, repositories never commit
- **Repositories** return domain entities, not ORM rows
- **Provider abstraction**: `TrackerProvider` is a `typing.Protocol`; `KeitaroProvider` implements it. Services depend only on the protocol
- **Schemas**: Pydantic models for API in/out, separate from ORM models and domain entities. Use `model_config = ConfigDict(from_attributes=True)` only at the API boundary
- **Errors**: services raise domain errors (`NotFoundError`, `ValidationError`, `ProviderError`); one exception handler maps them to HTTP responses with a consistent `{"detail": ..., "code": ...}` body
- **API**: REST under `/api/v1`, plural resource names, OpenAPI is the contract for the frontend
- **DB**: SQLAlchemy 2.0 typed models (`Mapped[...]`, `mapped_column`), a naming convention on `MetaData` for stable Alembic autogenerate, `timestamptz` columns, soft archive via `archived_at`
- **Logging**: structlog, JSON output in containers, request id bound per request

### Keitaro client
- Endpoint and payload reference: `docs/keitaro-api.md`. Read it before touching `providers/keitaro/`
- Admin API v1: `{KEITARO_BASE_URL}/admin_api/v1`, auth header `Api-Key: {KEITARO_API_KEY}`
- The instance is shared with other people: only modify or delete entities this app created
- `GET /offers` has no search; offers are cached briefly in the backend and filtered locally
- Single `httpx.AsyncClient` with `base_url`, auth header and a 10s timeout
- `tenacity` retries only idempotent GETs, and only on network errors and 5xx
- Responses are parsed into Pydantic DTOs with `extra="ignore"`; raw dicts never leave `providers/keitaro/`
- HTTP or API failures are converted to `ProviderError`
- Deleting an offer from a campaign means updating the offer stream without it. Never delete the offer entity itself
- The frontend never calls Keitaro; the backend is the only client

## Frontend (`frontend/`)

### Packages
| Purpose | Package |
|---|---|
| Build | `vite`, `@vitejs/plugin-react` |
| UI framework | `react` 19, `typescript` 6 (strict, `noUncheckedIndexedAccess`) |
| Styling | `tailwindcss` v4 (`@tailwindcss/vite`) |
| Components | `shadcn/ui` (`radix-nova` style, Radix primitives), `lucide-react`, `sonner` (toasts) |
| Routing | `react-router` v8 |
| Server state | `@tanstack/react-query` v5 |
| Forms | `react-hook-form`, `zod` v4, `@hookform/resolvers` |
| API client | `openapi-typescript` (codegen), `openapi-fetch` |
| Tests | `vitest`, `@testing-library/react`, `@testing-library/user-event`, `msw` v3 (`onUnhandledFrame`, not `onUnhandledRequest`) |
| Quality | `oxlint` (`.oxlintrc.json`), `prettier` + `prettier-plugin-tailwindcss` |

- Node 22+ is required (vitest, msw, jsdom, react-router). Run frontend tooling in the container if the host Node is older
- pnpm is pinned via `packageManager` in `package.json`
- TypeScript stays on 6.x: `openapi-typescript` needs the JS compiler API, which TypeScript 7 (native) does not provide
- Add shadcn components with `pnpm dlx shadcn@latest add <name>`

### Layout
```
frontend/src/
  app/              # App, providers (QueryClient, Tooltip, Toaster), routes, paths, layout
  test/             # vitest setup, msw server, render helpers
  components/ui/    # shadcn generated components, do not hand-edit
  components/       # shared app components
  features/
    campaigns/      # list page
    campaign-create/
    campaign-editor/
      api/          # query/mutation hooks
      components/
      model/        # draft reducer, share calculation, types
  lib/
    api/            # openapi-fetch client + generated schema.d.ts
    utils.ts
```

### Patterns
- **Typed API**: `pnpm gen:api` runs `openapi-typescript` against the backend `/openapi.json` to produce `lib/api/schema.d.ts`. Request and response types are never written by hand
- **Server state** lives only in TanStack Query: query key factories per feature, mutations invalidate affected keys
- **Editor draft state** is a `useReducer` inside `campaign-editor/model`, not global state. Actions: `add`, `archive`, `restore`, `togglePin`, `setShare`, `reset`. "Dirty" is derived by comparing the draft with server data
- **Share calculation** is a pure function, mirrored on the backend. The backend is authoritative and re-validates on push. Both sides are tested against the same fixture cases in `shared/share-cases.json`
- **Offer live search**: shadcn `Command` inside `Popover`, a `useDebouncedValue` hook (300ms), a query with `placeholderData: keepPreviousData`, and `enabled` only when the term has at least 2 characters
- **Forms**: react-hook-form + zod schema, shadcn `Field` components
- **Feedback**: `sonner` toasts for mutation results; `AlertDialog` to confirm discarding unpushed changes
- **Routes** are declared in `app/routes.tsx`; URLs are built only through `app/paths.ts`
- No `any`, no default exports (enforced by oxlint), components in PascalCase files

## Commands
- `docker compose up --build`: run the whole stack
- `docker compose exec backend uv run pytest`: backend tests
- `docker compose exec backend sh -c "uv run ruff check . && uv run ruff format --check . && uv run mypy app"`: backend lint and type check
- `docker compose exec backend uv run alembic revision --autogenerate -m "<msg>"`: new migration
- `docker compose exec backend uv run alembic upgrade head`: apply migrations
- `docker compose exec frontend pnpm test`: frontend tests
- `docker compose exec frontend sh -c "pnpm typecheck && pnpm lint && pnpm format:check"`: frontend checks
- `docker compose exec -e API_URL=http://backend:8000 frontend pnpm gen:api`: regenerate API types
