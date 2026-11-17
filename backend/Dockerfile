FROM python:3.12-slim AS base

COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app


FROM base AS dev

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen
COPY . .
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload --no-access-log"]


FROM base AS prod

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --no-dev --compile-bytecode
COPY . .
RUN useradd --create-home app
USER app
EXPOSE 8000
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --proxy-headers --no-access-log"]
