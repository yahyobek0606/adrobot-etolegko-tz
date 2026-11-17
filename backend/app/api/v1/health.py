from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel
from sqlalchemy import text

from app.core.dependencies import SessionDep

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ok"]


@router.get("", response_model=HealthResponse)
async def health(session: SessionDep) -> HealthResponse:
    await session.execute(text("SELECT 1"))
    return HealthResponse(status="ok", database="ok")
