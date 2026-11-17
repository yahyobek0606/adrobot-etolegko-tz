from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.dependencies import get_provider
from tests.fakes import FakeTrackerProvider

VALID_PAYLOAD = {
    "name": "  My campaign ",
    "countries": ["au", "MX", "AU"],
    "offer_id": 13972,
    "domain_id": 1813,
    "group_id": 10332,
    "traffic_source_id": 836,
}


@pytest.fixture
def fake_provider(app: FastAPI) -> Iterator[FakeTrackerProvider]:
    provider = FakeTrackerProvider()
    app.dependency_overrides[get_provider] = lambda: provider
    yield provider
    app.dependency_overrides.pop(get_provider, None)


async def test_form_options(client: AsyncClient, fake_provider: FakeTrackerProvider) -> None:
    response = await client.get("/api/v1/campaigns/form-options")

    assert response.status_code == 200
    body = response.json()
    assert body["domains"] == [{"id": 1813, "name": "kylovoa.com"}]
    assert body["groups"] == [{"id": 10332, "name": "FORTESTS"}]
    assert body["traffic_sources"] == [{"id": 836, "name": "FORTESTS"}]
    assert set(body["defaults"]) == {"domain_id", "group_id", "traffic_source_id"}
    assert body["fallback_redirect_url"].startswith("https://")


async def test_search_offers(client: AsyncClient, fake_provider: FakeTrackerProvider) -> None:
    response = await client.get("/api/v1/offers", params={"query": "miaflow"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 13972, "name": "13972 Miaflow [BEAUTY-RO]", "group": "RO", "countries": ["Romania"]}
    ]


async def test_create_campaign(client: AsyncClient, fake_provider: FakeTrackerProvider) -> None:
    response = await client.post("/api/v1/campaigns", json=VALID_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "My campaign"
    assert body["alias"].startswith("my-campaign-")
    assert body["admin_url"] == f"https://tracker.test/admin/#!/campaign/{body['id']}/main"
    geo, _ = await fake_provider.list_streams(body["id"])
    assert geo.countries == ["AU", "MX"]

    listed = await client.get("/api/v1/campaigns")
    assert [campaign["id"] for campaign in listed.json()] == [body["id"]]


@pytest.mark.parametrize(
    "override",
    [
        {"countries": []},
        {"countries": ["AUS"]},
        {"countries": ["ZZ"]},
        {"name": "   "},
        {"offer_id": 0},
    ],
)
async def test_create_campaign_validation(
    client: AsyncClient, fake_provider: FakeTrackerProvider, override: dict[str, object]
) -> None:
    response = await client.post("/api/v1/campaigns", json={**VALID_PAYLOAD, **override})

    assert response.status_code == 422
    assert fake_provider.campaigns == {}


async def test_create_campaign_unknown_offer(
    client: AsyncClient, fake_provider: FakeTrackerProvider
) -> None:
    response = await client.post("/api/v1/campaigns", json={**VALID_PAYLOAD, "offer_id": 999})

    assert response.status_code == 404
    assert response.json() == {"detail": "Offer 999 not found", "code": "not_found"}


async def test_provider_failure_maps_to_bad_gateway(
    client: AsyncClient, fake_provider: FakeTrackerProvider
) -> None:
    fake_provider.fail_on.add("create_campaign")

    response = await client.post("/api/v1/campaigns", json=VALID_PAYLOAD)

    assert response.status_code == 502
    assert response.json()["code"] == "provider_error"
