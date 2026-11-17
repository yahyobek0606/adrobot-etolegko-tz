from collections.abc import Sequence
from dataclasses import replace

from app.domain.errors import NotFoundError, ProviderError
from app.providers.base import (
    Campaign,
    NamedRef,
    NewCampaign,
    NewGeoRedirectStream,
    NewOffersStream,
    Offer,
    Stream,
    StreamKind,
    StreamOffer,
)


class FakeTrackerProvider:
    def __init__(self) -> None:
        self.domains = [NamedRef(1813, "kylovoa.com")]
        self.groups = [NamedRef(10332, "FORTESTS")]
        self.traffic_sources = [NamedRef(836, "FORTESTS")]
        self.offers = [
            Offer(13972, "13972 Miaflow [BEAUTY-RO]", "RO", ["Romania"], True),
            Offer(3749, "3749 Flexacil [JOINT-PE]", None, [], True),
        ]
        self.campaigns: dict[int, Campaign] = {}
        self.archived_campaign_ids: list[int] = []
        self.streams: dict[int, Stream] = {}
        self.fail_on: set[str] = set()
        self._next_id = 100

    def _fail_if_requested(self, operation: str) -> None:
        if operation in self.fail_on:
            raise ProviderError(f"{operation} failed")

    def _new_id(self) -> int:
        self._next_id += 1
        return self._next_id

    async def list_domains(self) -> list[NamedRef]:
        return self.domains

    async def list_campaign_groups(self) -> list[NamedRef]:
        return self.groups

    async def list_traffic_sources(self) -> list[NamedRef]:
        return self.traffic_sources

    async def search_offers(self, query: str, limit: int) -> list[Offer]:
        needle = query.casefold()
        return [offer for offer in self.offers if needle in offer.name.casefold()][:limit]

    async def get_offers(self, offer_ids: Sequence[int]) -> list[Offer]:
        return [offer for offer in self.offers if offer.id in offer_ids]

    async def list_campaigns(self) -> list[Campaign]:
        return list(self.campaigns.values())

    async def get_campaign(self, campaign_id: int) -> Campaign:
        if campaign_id not in self.campaigns:
            raise NotFoundError(f"Campaign {campaign_id} not found")
        return self.campaigns[campaign_id]

    async def create_campaign(self, campaign: NewCampaign) -> Campaign:
        self._fail_if_requested("create_campaign")
        created = Campaign(
            id=self._new_id(),
            name=campaign.name,
            alias=campaign.alias,
            is_active=True,
            tracking_url=f"https://kylovoa.com/{campaign.alias}",
            domain_id=campaign.domain_id,
            group_id=campaign.group_id,
            traffic_source_id=campaign.traffic_source_id,
        )
        self.campaigns[created.id] = created
        return created

    async def archive_campaign(self, campaign_id: int) -> None:
        self._fail_if_requested("archive_campaign")
        self.archived_campaign_ids.append(campaign_id)
        self.campaigns.pop(campaign_id, None)

    async def list_streams(self, campaign_id: int) -> list[Stream]:
        streams = [s for s in self.streams.values() if s.campaign_id == campaign_id]
        return sorted(streams, key=lambda s: s.position)

    async def create_geo_redirect_stream(self, stream: NewGeoRedirectStream) -> Stream:
        self._fail_if_requested("create_geo_redirect_stream")
        created = Stream(
            id=self._new_id(),
            campaign_id=stream.campaign_id,
            name=stream.name,
            position=stream.position,
            kind=StreamKind.GEO_REDIRECT,
            countries=stream.countries,
            redirect_url=stream.redirect_url,
        )
        self.streams[created.id] = created
        return created

    async def create_offers_stream(self, stream: NewOffersStream) -> Stream:
        self._fail_if_requested("create_offers_stream")
        created = Stream(
            id=self._new_id(),
            campaign_id=stream.campaign_id,
            name=stream.name,
            position=stream.position,
            kind=StreamKind.OFFERS,
            offers=stream.offers,
        )
        self.streams[created.id] = created
        return created

    async def replace_stream_offers(self, stream_id: int, offers: Sequence[StreamOffer]) -> Stream:
        self._fail_if_requested("replace_stream_offers")
        updated = replace(self.streams[stream_id], offers=list(offers))
        self.streams[stream_id] = updated
        return updated

    def campaign_admin_url(self, campaign_id: int) -> str:
        return f"https://tracker.test/admin/#!/campaign/{campaign_id}/main"
