from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.errors import (
    ConflictError,
    DomainError,
    InvalidOperationError,
    NotFoundError,
    ProviderError,
)

STATUS_BY_ERROR: dict[type[DomainError], int] = {
    NotFoundError: status.HTTP_404_NOT_FOUND,
    InvalidOperationError: status.HTTP_422_UNPROCESSABLE_CONTENT,
    ConflictError: status.HTTP_409_CONFLICT,
    ProviderError: status.HTTP_502_BAD_GATEWAY,
}


def _status_for(error: DomainError) -> int:
    for error_type in type(error).__mro__:
        if error_type in STATUS_BY_ERROR:
            return STATUS_BY_ERROR[error_type]
    return status.HTTP_400_BAD_REQUEST


async def domain_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, DomainError)
    return JSONResponse(
        status_code=_status_for(exc),
        content={"detail": exc.message, "code": exc.code},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(DomainError, domain_error_handler)
