from collections.abc import AsyncIterator

import asyncpg
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.settings import Settings, get_settings
from app.db.models import Base
from app.main import create_app

TEST_DATABASE_SUFFIX = "_test"


@pytest.fixture(scope="session")
def settings() -> Settings:
    base = get_settings()
    url = make_url(base.database_url)
    test_url = url.set(database=f"{url.database}{TEST_DATABASE_SUFFIX}")
    return base.model_copy(update={"database_url": test_url.render_as_string(hide_password=False)})


@pytest.fixture(scope="session")
async def database(settings: Settings) -> AsyncIterator[str]:
    url = make_url(settings.database_url)
    admin = await asyncpg.connect(
        user=url.username,
        password=url.password,
        host=url.host,
        port=url.port or 5432,
        database="postgres",
    )
    try:
        exists = await admin.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", url.database)
        if not exists:
            await admin.execute(f'CREATE DATABASE "{url.database}"')
    finally:
        await admin.close()

    engine = create_async_engine(settings.database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield settings.database_url
    await engine.dispose()


@pytest.fixture(scope="session")
def app(settings: Settings, database: str) -> FastAPI:
    return create_app(settings)


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with (
        app.router.lifespan_context(app),
        AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client,
    ):
        yield client
        tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
        async with app.state.database.engine.begin() as connection:
            await connection.execute(text(f"TRUNCATE {tables} RESTART IDENTITY"))
