from collections.abc import AsyncIterator, Iterator

import httpx
import pytest
import respx

from app.providers.keitaro.client import KeitaroClient
from app.providers.keitaro.provider import KeitaroProvider

BASE_URL = "https://tracker.test"
API_URL = f"{BASE_URL}/admin_api/v1"


@pytest.fixture
def keitaro_api() -> Iterator[respx.MockRouter]:
    with respx.mock(base_url=API_URL, assert_all_called=False) as router:
        yield router


@pytest.fixture
async def keitaro_client(keitaro_api: respx.MockRouter) -> AsyncIterator[KeitaroClient]:
    async with httpx.AsyncClient(base_url=BASE_URL) as http:
        yield KeitaroClient(http, max_attempts=3, backoff_seconds=0)


@pytest.fixture
def provider(keitaro_client: KeitaroClient) -> KeitaroProvider:
    return KeitaroProvider(keitaro_client, admin_base_url=BASE_URL)
