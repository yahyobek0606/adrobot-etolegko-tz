import httpx

from app.core.settings import Settings
from app.providers.keitaro.client import KeitaroClient
from app.providers.keitaro.provider import KeitaroProvider


def create_keitaro_http_client(settings: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=str(settings.keitaro_base_url).rstrip("/"),
        headers={
            "Api-Key": settings.keitaro_api_key.get_secret_value(),
            "Accept": "application/json",
        },
        timeout=settings.keitaro_timeout_seconds,
    )


def create_keitaro_provider(settings: Settings, http: httpx.AsyncClient) -> KeitaroProvider:
    return KeitaroProvider(
        client=KeitaroClient(http),
        admin_base_url=str(settings.keitaro_base_url),
        offers_ttl_seconds=settings.keitaro_offers_ttl_seconds,
    )
