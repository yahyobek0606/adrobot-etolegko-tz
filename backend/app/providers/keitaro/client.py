from typing import Any

import httpx
import structlog
from tenacity import (
    AsyncRetrying,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from app.domain.errors import NotFoundError, ProviderError

API_PREFIX = "/admin_api/v1"

logger = structlog.get_logger()


def _is_retryable(error: BaseException) -> bool:
    if isinstance(error, httpx.TransportError):
        return True
    return isinstance(error, httpx.HTTPStatusError) and error.response.status_code >= 500


class KeitaroClient:
    def __init__(
        self, http: httpx.AsyncClient, max_attempts: int = 3, backoff_seconds: float = 0.2
    ) -> None:
        self._http = http
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        retrying = AsyncRetrying(
            retry=retry_if_exception(_is_retryable),
            stop=stop_after_attempt(self._max_attempts),
            wait=wait_exponential(multiplier=self._backoff_seconds, max=2),
            reraise=True,
        )
        try:
            async for attempt in retrying:
                with attempt:
                    return await self._send("GET", path, params=params)
        except httpx.HTTPError as error:
            raise self._to_domain_error("GET", path, error) from error
        raise AssertionError("unreachable")

    async def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return await self._send_once("POST", path, body)

    async def put(self, path: str, body: dict[str, Any]) -> Any:
        return await self._send_once("PUT", path, body)

    async def delete(self, path: str) -> Any:
        return await self._send_once("DELETE", path)

    async def _send_once(self, method: str, path: str, body: dict[str, Any] | None = None) -> Any:
        try:
            return await self._send(method, path, json=body)
        except httpx.HTTPError as error:
            raise self._to_domain_error(method, path, error) from error

    async def _send(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> Any:
        response = await self._http.request(method, f"{API_PREFIX}{path}", params=params, json=json)
        response.raise_for_status()
        return response.json() if response.content else None

    @staticmethod
    def _to_domain_error(method: str, path: str, error: httpx.HTTPError) -> Exception:
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code
            logger.warning(
                "keitaro_request_failed",
                method=method,
                path=path,
                status=status,
                body=error.response.text[:500],
            )
            if status == 404:
                return NotFoundError(f"Keitaro resource not found: {path}")
            return ProviderError(f"Keitaro responded with {status} for {method} {path}")
        logger.warning("keitaro_unreachable", method=method, path=path, error=str(error))
        return ProviderError(f"Keitaro is unreachable: {error}")
