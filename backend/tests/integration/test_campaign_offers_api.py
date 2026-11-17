from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.dependencies import get_provider
from app.providers.base import (
    NewCampaign,
    NewGeoRedirectStream,
    NewOffersStream,
    StreamOffer,
)
from tests.fakes import FakeTrackerProvider

FLEX, MIA = 3749, 13972


@pytest.fixture
def provider(app: FastAPI) -> Iterator[FakeTrackerProvider]:
    fake = FakeTrackerProvider()
    app.dependency_overrides[get_provider] = lambda: fake
    yield fake
    app.dependency_overrides.pop(get_provider, None)


@pytest.fixture
async def campaign_id(provider: FakeTrackerProvider) -> int:
    campaign = await provider.create_campaign(
        NewCampaign(name="C", alias="c", domain_id=1, group_id=1, traffic_source_id=1)
    )
    await provider.create_geo_redirect_stream(
        NewGeoRedirectStream(campaign.id, "Geo", 1, ["AU"], "https://google.com")
    )
    await provider.create_offers_stream(
        NewOffersStream(campaign.id, "Offers", 2, [StreamOffer(MIA, 100)])
    )
    return campaign.id


def stream_offers(provider: FakeTrackerProvider, campaign_id: int) -> list[tuple[int, int]]:
    stream = next(s for s in provider.streams.values() if s.campaign_id == campaign_id and s.offers)
    return [(o.offer_id, o.share) for o in stream.offers]


async def revision(client: AsyncClient, campaign_id: int) -> str:
    response = await client.get(f"/api/v1/campaigns/{campaign_id}/offers")
    value: str = response.json()["revision"]
    return value


def rows(body: dict[str, Any]) -> list[tuple[int, int, bool, bool]]:
    return [(o["offer_id"], o["share"], o["is_pinned"], o["is_archived"]) for o in body["offers"]]


async def test_first_open_imports_offers_from_provider(
    client: AsyncClient, provider: FakeTrackerProvider, campaign_id: int
) -> None:
    response = await client.get(f"/api/v1/campaigns/{campaign_id}/offers")

    assert response.status_code == 200
    body = response.json()
    assert body["campaign"]["id"] == campaign_id
    assert body["stream"]["name"] == "Offers"
    assert body["offers"] == [
        {
            "offer_id": MIA,
            "name": "13972 Miaflow [BEAUTY-RO]",
            "share": 100,
            "is_pinned": False,
            "is_archived": False,
        }
    ]


async def test_push_updates_provider_and_keeps_archive_and_pins(
    client: AsyncClient, provider: FakeTrackerProvider, campaign_id: int
) -> None:
    response = await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={
            "offers": [
                {"offer_id": MIA, "share": 30, "is_pinned": True, "is_archived": False},
                {"offer_id": FLEX, "share": 0, "is_pinned": False, "is_archived": False},
            ],
            "revision": await revision(client, campaign_id),
        },
    )

    assert response.status_code == 200
    assert rows(response.json()) == [(MIA, 30, True, False), (FLEX, 70, False, False)]
    assert stream_offers(provider, campaign_id) == [(MIA, 30), (FLEX, 70)]

    archived = await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={
            "offers": [
                {"offer_id": MIA, "share": 30, "is_pinned": True, "is_archived": True},
                {"offer_id": FLEX, "share": 70, "is_pinned": False, "is_archived": False},
            ],
            "revision": response.json()["revision"],
        },
    )

    assert rows(archived.json()) == [(MIA, 30, False, True), (FLEX, 100, False, False)]
    assert stream_offers(provider, campaign_id) == [(FLEX, 100)]

    reloaded = await client.get(f"/api/v1/campaigns/{campaign_id}/offers")
    assert rows(reloaded.json()) == [(MIA, 30, False, True), (FLEX, 100, False, False)]


async def test_sync_archives_offers_removed_in_provider(
    client: AsyncClient, provider: FakeTrackerProvider, campaign_id: int
) -> None:
    await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={
            "offers": [
                {"offer_id": MIA, "share": 50, "is_pinned": False, "is_archived": False},
                {"offer_id": FLEX, "share": 50, "is_pinned": False, "is_archived": False},
            ],
            "revision": await revision(client, campaign_id),
        },
    )
    stream_id = next(s.id for s in provider.streams.values() if s.offers)
    await provider.replace_stream_offers(stream_id, [StreamOffer(FLEX, 100)])

    response = await client.post(f"/api/v1/campaigns/{campaign_id}/offers/sync")

    assert response.status_code == 200
    assert rows(response.json()) == [(FLEX, 100, False, False), (MIA, 50, False, True)]


@pytest.mark.parametrize(
    ("offers", "status", "code"),
    [
        (
            [{"offer_id": MIA, "share": 60, "is_pinned": True, "is_archived": False}],
            422,
            "invalid_operation",
        ),
        (
            [{"offer_id": 999, "share": 0, "is_pinned": False, "is_archived": False}],
            404,
            "not_found",
        ),
    ],
)
async def test_push_rejects_invalid_drafts_without_touching_provider(
    client: AsyncClient,
    provider: FakeTrackerProvider,
    campaign_id: int,
    offers: list[dict[str, Any]],
    status: int,
    code: str,
) -> None:
    response = await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={"offers": offers, "revision": await revision(client, campaign_id)},
    )

    assert response.status_code == status
    assert response.json()["code"] == code
    assert stream_offers(provider, campaign_id) == [(MIA, 100)]


async def test_provider_failure_does_not_change_local_state(
    client: AsyncClient, provider: FakeTrackerProvider, campaign_id: int
) -> None:
    loaded = await revision(client, campaign_id)
    provider.fail_on.add("replace_stream_offers")

    response = await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={
            "offers": [{"offer_id": FLEX, "share": 0, "is_pinned": False, "is_archived": False}],
            "revision": loaded,
        },
    )

    assert response.status_code == 502
    reloaded = await client.get(f"/api/v1/campaigns/{campaign_id}/offers")
    assert rows(reloaded.json()) == [(MIA, 100, False, False)]


async def test_push_refuses_to_overwrite_changes_made_in_provider(
    client: AsyncClient, provider: FakeTrackerProvider, campaign_id: int
) -> None:
    loaded = await revision(client, campaign_id)
    stream_id = next(s.id for s in provider.streams.values() if s.offers)
    await provider.replace_stream_offers(stream_id, [StreamOffer(FLEX, 100)])

    response = await client.put(
        f"/api/v1/campaigns/{campaign_id}/offers",
        json={
            "offers": [{"offer_id": MIA, "share": 0, "is_pinned": False, "is_archived": False}],
            "revision": loaded,
        },
    )

    assert response.status_code == 409
    assert response.json()["code"] == "conflict"
    assert stream_offers(provider, campaign_id) == [(FLEX, 100)]


async def test_unknown_campaign(client: AsyncClient, provider: FakeTrackerProvider) -> None:
    response = await client.get("/api/v1/campaigns/424242/offers")

    assert response.status_code == 404
