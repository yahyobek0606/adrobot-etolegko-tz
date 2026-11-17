from collections.abc import Sequence

from pydantic import TypeAdapter

from app.core.cache import AsyncTtlValue
from app.domain.errors import NotFoundError
from app.providers.base import (
    Campaign,
    NamedRef,
    NewCampaign,
    NewGeoRedirectStream,
    NewOffersStream,
    Offer,
    Stream,
    StreamOffer,
)
from app.providers.keitaro.client import KeitaroClient
from app.providers.keitaro.mappers import (
    COUNTRY_FILTER,
    LANDINGS_SCHEMA,
    REDIRECT_SCHEMA,
    stream_offers_payload,
    to_campaign,
    to_named_ref,
    to_offer,
    to_stream,
)
from app.providers.keitaro.schemas import (
    KeitaroCampaign,
    KeitaroNamed,
    KeitaroOffer,
    KeitaroStream,
)

HTTP_REDIRECT_ACTION = "http"
REGULAR_STREAM = "regular"
DEFAULT_STREAM = "default"

_named_list = TypeAdapter(list[KeitaroNamed])
_offer_list = TypeAdapter(list[KeitaroOffer])
_campaign_list = TypeAdapter(list[KeitaroCampaign])
_stream_list = TypeAdapter(list[KeitaroStream])


class KeitaroProvider:
    def __init__(
        self,
        client: KeitaroClient,
        admin_base_url: str,
        offers_ttl_seconds: float = 60.0,
    ) -> None:
        self._client = client
        self._admin_base_url = admin_base_url.rstrip("/")
        self._offers = AsyncTtlValue(self._load_offers, offers_ttl_seconds)

    async def list_domains(self) -> list[NamedRef]:
        return await self._list_named("/domains")

    async def list_campaign_groups(self) -> list[NamedRef]:
        return await self._list_named("/groups", params={"type": "campaigns"})

    async def list_traffic_sources(self) -> list[NamedRef]:
        return await self._list_named("/traffic_sources")

    async def search_offers(self, query: str, limit: int) -> list[Offer]:
        needle = query.strip().casefold()
        offers = [offer for offer in await self._offers.get() if offer.is_active]
        if needle:
            offers = [
                offer
                for offer in offers
                if needle in offer.name.casefold() or needle == str(offer.id)
            ]
        return offers[:limit]

    async def get_offers(self, offer_ids: Sequence[int]) -> list[Offer]:
        wanted = set(offer_ids)
        return [offer for offer in await self._offers.get() if offer.id in wanted]

    async def list_campaigns(self) -> list[Campaign]:
        raw = _campaign_list.validate_python(await self._client.get("/campaigns"))
        return [to_campaign(campaign) for campaign in raw]

    async def get_campaign(self, campaign_id: int) -> Campaign:
        raw = await self._client.get(f"/campaigns/{campaign_id}")
        if not raw:
            raise NotFoundError(f"Campaign {campaign_id} not found")
        return to_campaign(KeitaroCampaign.model_validate(raw))

    async def create_campaign(self, campaign: NewCampaign) -> Campaign:
        raw = await self._client.post(
            "/campaigns",
            {
                "name": campaign.name,
                "alias": campaign.alias,
                "type": "position",
                "state": "active",
                "domain_id": campaign.domain_id,
                "group_id": str(campaign.group_id),
                "traffic_source_id": campaign.traffic_source_id,
            },
        )
        return to_campaign(KeitaroCampaign.model_validate(raw))

    async def archive_campaign(self, campaign_id: int) -> None:
        await self._client.delete(f"/campaigns/{campaign_id}")

    async def list_streams(self, campaign_id: int) -> list[Stream]:
        raw = _stream_list.validate_python(
            await self._client.get(f"/campaigns/{campaign_id}/streams")
        )
        return sorted((to_stream(stream) for stream in raw), key=lambda s: s.position)

    async def create_geo_redirect_stream(self, stream: NewGeoRedirectStream) -> Stream:
        return await self._create_stream(
            {
                "campaign_id": stream.campaign_id,
                "type": REGULAR_STREAM,
                "name": stream.name,
                "position": stream.position,
                "state": "active",
                "schema": REDIRECT_SCHEMA,
                "action_type": HTTP_REDIRECT_ACTION,
                "action_payload": stream.redirect_url,
                "filters": [
                    {"name": COUNTRY_FILTER, "mode": "accept", "payload": stream.countries}
                ],
            }
        )

    async def create_offers_stream(self, stream: NewOffersStream) -> Stream:
        return await self._create_stream(
            {
                "campaign_id": stream.campaign_id,
                "type": DEFAULT_STREAM,
                "name": stream.name,
                "position": stream.position,
                "state": "active",
                "schema": LANDINGS_SCHEMA,
                "action_type": HTTP_REDIRECT_ACTION,
                "offers": stream_offers_payload(stream.offers),
            }
        )

    async def replace_stream_offers(self, stream_id: int, offers: Sequence[StreamOffer]) -> Stream:
        raw = await self._client.put(
            f"/streams/{stream_id}", {"offers": stream_offers_payload(list(offers))}
        )
        return to_stream(KeitaroStream.model_validate(raw))

    def campaign_admin_url(self, campaign_id: int) -> str:
        return f"{self._admin_base_url}/admin/#!/campaign/{campaign_id}/main"

    async def _create_stream(self, body: dict[str, object]) -> Stream:
        raw = await self._client.post("/streams", body)
        return to_stream(KeitaroStream.model_validate(raw))

    async def _list_named(self, path: str, params: dict[str, str] | None = None) -> list[NamedRef]:
        raw = _named_list.validate_python(await self._client.get(path, params=params))
        return [to_named_ref(item) for item in raw]

    async def _load_offers(self) -> list[Offer]:
        raw = _offer_list.validate_python(await self._client.get("/offers"))
        return [to_offer(offer) for offer in raw]
