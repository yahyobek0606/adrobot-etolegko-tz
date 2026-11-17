from app.core.cache import AsyncTtlValue


async def test_value_is_cached_until_ttl_expires() -> None:
    now = 0.0
    loads = 0

    async def loader() -> int:
        nonlocal loads
        loads += 1
        return loads

    cache = AsyncTtlValue(loader, ttl_seconds=10, clock=lambda: now)

    assert await cache.get() == 1
    now = 9.9
    assert await cache.get() == 1
    now = 10.0
    assert await cache.get() == 2

    cache.invalidate()
    assert await cache.get() == 3
