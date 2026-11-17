import httpx
import pytest
import respx

from app.domain.errors import NotFoundError, ProviderError
from app.providers.keitaro.client import KeitaroClient


async def test_get_retries_server_errors(
    keitaro_api: respx.MockRouter, keitaro_client: KeitaroClient
) -> None:
    route = keitaro_api.get("/domains").mock(
        side_effect=[httpx.Response(502), httpx.Response(200, json=[{"id": 1}])]
    )

    assert await keitaro_client.get("/domains") == [{"id": 1}]
    assert route.call_count == 2


async def test_get_gives_up_after_max_attempts(
    keitaro_api: respx.MockRouter, keitaro_client: KeitaroClient
) -> None:
    route = keitaro_api.get("/domains").mock(return_value=httpx.Response(500))

    with pytest.raises(ProviderError):
        await keitaro_client.get("/domains")
    assert route.call_count == 3


async def test_get_does_not_retry_client_errors(
    keitaro_api: respx.MockRouter, keitaro_client: KeitaroClient
) -> None:
    route = keitaro_api.get("/campaigns/1").mock(return_value=httpx.Response(404))

    with pytest.raises(NotFoundError):
        await keitaro_client.get("/campaigns/1")
    assert route.call_count == 1


async def test_writes_are_never_retried(
    keitaro_api: respx.MockRouter, keitaro_client: KeitaroClient
) -> None:
    route = keitaro_api.post("/campaigns").mock(return_value=httpx.Response(503))

    with pytest.raises(ProviderError):
        await keitaro_client.post("/campaigns", {"name": "x"})
    assert route.call_count == 1


async def test_network_errors_become_provider_errors(
    keitaro_api: respx.MockRouter, keitaro_client: KeitaroClient
) -> None:
    keitaro_api.put("/streams/1").mock(side_effect=httpx.ConnectError("boom"))

    with pytest.raises(ProviderError, match="unreachable"):
        await keitaro_client.put("/streams/1", {"offers": []})
