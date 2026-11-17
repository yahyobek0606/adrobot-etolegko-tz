from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings, get_settings
from app.db.session import Database


def get_database(request: Request) -> Database:
    database: Database = request.app.state.database
    return database


async def get_session(
    database: Annotated[Database, Depends(get_database)],
) -> AsyncIterator[AsyncSession]:
    async for session in database.session():
        yield session


SettingsDep = Annotated[Settings, Depends(get_settings)]
SessionDep = Annotated[AsyncSession, Depends(get_session)]
