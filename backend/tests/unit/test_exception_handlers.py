import pytest
from fastapi import status

from app.core.exception_handlers import domain_error_handler
from app.domain.errors import (
    ConflictError,
    DomainError,
    InvalidOperationError,
    NotFoundError,
    ProviderError,
)


@pytest.mark.parametrize(
    ("error", "expected_status"),
    [
        (NotFoundError("missing"), status.HTTP_404_NOT_FOUND),
        (InvalidOperationError("bad"), status.HTTP_422_UNPROCESSABLE_CONTENT),
        (ConflictError("conflict"), status.HTTP_409_CONFLICT),
        (ProviderError("down"), status.HTTP_502_BAD_GATEWAY),
        (DomainError("generic"), status.HTTP_400_BAD_REQUEST),
    ],
)
async def test_domain_errors_map_to_http(error: DomainError, expected_status: int) -> None:
    response = await domain_error_handler(None, error)  # type: ignore[arg-type]

    assert response.status_code == expected_status
    assert response.body == (f'{{"detail":"{error.message}","code":"{error.code}"}}'.encode())
