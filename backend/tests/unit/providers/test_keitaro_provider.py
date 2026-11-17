import json

import httpx
import respx

from app.providers.base import (
    NewCampaign,
    NewGeoRedirectStream,
    NewOffersStream,
    StreamKind,
    StreamOffer,
)
from app.providers.keitaro.provider import KeitaroProvider

OFFERS = [
    {
        "id": 13972,
        "name": "13972 Miaflow [BEAUTY-RO]",
        "group": "RO",
        "country": ["Romania"],
        "state": "active",
        "payout_value": 0,
    },
    {"id": 3749, "name": "3749 Flexacil [JOINT-PE]", "group": "", "country": [], "state": "active"},
    {"id": 1, "name": "1 Old Miaflow", "group": None, "country": [], "state": "deleted"},
    {"id": 2, "name": "2 No Country", "group": "X", "country": "", "state": "active"},
]

GEO_STREAM = {
    "id": 10,
    "type": "regular",
    "name": "Geo",
    "campaign_id": 5,
    "position": 1,
    "action_type": "http",
    "action_payload": "https://www.google.com/",
    "schema": "redirect",
    "filters": [{"id": 1, "name": "country", "mode": "accept", "payload": ["AU"]}],
    "offers": [],
}
OFFERS_STREAM = {
    "id": 11,
    "type": "default",
    "name": "Offers",
    "campaign_id": 5,
    "position": 2,
    "action_type": "http",
    "action_payload": "",
    "schema": "landings",
    "filters": [],
    "offers": [{"id": 7, "stream_id": 11, "offer_id": 13972, "share": 100, "state": "active"}],
}
CAMPAIGN = {
    "id": 5,
    "alias": "my-campaign-ab12",
    "name": "My campaign",
    "state": "active",
    "domain_id": 1813,
    "domain": "https://kylovoa.com/",
    "group_id": 10332,
    "traffic_source_id": 836,
    "type": "position",
}


async def test_search_offers_filters_active_by_name_and_caches(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    route = keitaro_api.get("/offers").mock(return_value=httpx.Response(200, json=OFFERS))

    found = await provider.search_offers("miaflow", limit=10)
    by_id = await provider.search_offers("3749", limit=10)

    assert [offer.id for offer in found] == [13972]
    assert [offer.id for offer in by_id] == [3749]
    assert found[0].countries == ["Romania"]
    assert route.call_count == 1


async def test_search_offers_respects_limit(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    keitaro_api.get("/offers").mock(return_value=httpx.Response(200, json=OFFERS))

    assert len(await provider.search_offers("", limit=1)) == 1


async def test_list_streams_maps_kinds_and_sorts(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    keitaro_api.get("/campaigns/5/streams").mock(
        return_value=httpx.Response(200, json=[OFFERS_STREAM, GEO_STREAM])
    )

    geo, offers = await provider.list_streams(5)

    assert geo.kind is StreamKind.GEO_REDIRECT
    assert geo.countries == ["AU"]
    assert geo.redirect_url == "https://www.google.com/"
    assert offers.kind is StreamKind.OFFERS
    assert offers.offers == [StreamOffer(offer_id=13972, share=100)]


async def test_create_campaign_sends_expected_body(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    route = keitaro_api.post("/campaigns").mock(return_value=httpx.Response(200, json=CAMPAIGN))

    campaign = await provider.create_campaign(
        NewCampaign(
            name="My campaign",
            alias="my-campaign-ab12",
            domain_id=1813,
            group_id=10332,
            traffic_source_id=836,
        )
    )

    assert json.loads(route.calls.last.request.content) == {
        "name": "My campaign",
        "alias": "my-campaign-ab12",
        "type": "position",
        "state": "active",
        "domain_id": 1813,
        "group_id": "10332",
        "traffic_source_id": 836,
    }
    assert campaign.tracking_url == "https://kylovoa.com/my-campaign-ab12"


async def test_create_geo_redirect_stream_body(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    route = keitaro_api.post("/streams").mock(return_value=httpx.Response(200, json=GEO_STREAM))

    await provider.create_geo_redirect_stream(
        NewGeoRedirectStream(
            campaign_id=5,
            name="Geo",
            position=1,
            countries=["AU", "MX"],
            redirect_url="https://google.com",
        )
    )

    body = json.loads(route.calls.last.request.content)
    assert body["type"] == "regular"
    assert body["schema"] == "redirect"
    assert body["action_type"] == "http"
    assert body["action_payload"] == "https://google.com"
    assert body["filters"] == [{"name": "country", "mode": "accept", "payload": ["AU", "MX"]}]


async def test_create_offers_stream_body(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    route = keitaro_api.post("/streams").mock(return_value=httpx.Response(200, json=OFFERS_STREAM))

    await provider.create_offers_stream(
        NewOffersStream(
            campaign_id=5,
            name="Offers",
            position=2,
            offers=[StreamOffer(offer_id=13972, share=100)],
        )
    )

    body = json.loads(route.calls.last.request.content)
    assert body["type"] == "default"
    assert body["schema"] == "landings"
    assert body["offers"] == [{"offer_id": 13972, "share": 100, "state": "active"}]


async def test_replace_stream_offers_sends_full_list(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    route = keitaro_api.put("/streams/11").mock(
        return_value=httpx.Response(200, json=OFFERS_STREAM)
    )

    await provider.replace_stream_offers(
        11, [StreamOffer(offer_id=1, share=60), StreamOffer(offer_id=2, share=40)]
    )

    assert json.loads(route.calls.last.request.content) == {
        "offers": [
            {"offer_id": 1, "share": 60, "state": "active"},
            {"offer_id": 2, "share": 40, "state": "active"},
        ]
    }


async def test_offer_with_empty_country_string(
    keitaro_api: respx.MockRouter, provider: KeitaroProvider
) -> None:
    keitaro_api.get("/offers").mock(return_value=httpx.Response(200, json=OFFERS))

    (offer,) = await provider.get_offers([2])

    assert offer.countries == []


def test_campaign_admin_url(provider: KeitaroProvider) -> None:
    assert provider.campaign_admin_url(5) == "https://tracker.test/admin/#!/campaign/5/main"
