import asyncio
import time
from collections.abc import Awaitable, Callable


class AsyncTtlValue[T]:
    def __init__(
        self,
        loader: Callable[[], Awaitable[T]],
        ttl_seconds: float,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._loader = loader
        self._ttl = ttl_seconds
        self._clock = clock
        self._lock = asyncio.Lock()
        self._value: T | None = None
        self._expires_at = 0.0

    async def get(self) -> T:
        if self._value is not None and self._clock() < self._expires_at:
            return self._value
        async with self._lock:
            if self._value is None or self._clock() >= self._expires_at:
                self._value = await self._loader()
                self._expires_at = self._clock() + self._ttl
            return self._value

    def invalidate(self) -> None:
        self._value = None
        self._expires_at = 0.0
