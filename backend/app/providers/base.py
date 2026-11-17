from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Protocol


class StreamKind(StrEnum):
    GEO_REDIRECT = "geo_redirect"
    OFFERS = "offers"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class NamedRef:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Offer:
    id: int
    name: str
    group: str | None
    countries: list[str]
    is_active: bool


@dataclass(frozen=True, slots=True)
class Campaign:
    id: int
    name: str
    alias: str
    is_active: bool
    tracking_url: str
    domain_id: int | None
    group_id: int | None
    traffic_source_id: int | None


@dataclass(frozen=True, slots=True)
class StreamOffer:
    offer_id: int
    share: int
    is_active: bool = True


@dataclass(frozen=True, slots=True)
class Stream:
    id: int
    campaign_id: int
    name: str
    position: int
    kind: StreamKind
    countries: list[str] = field(default_factory=list)
    redirect_url: str | None = None
    offers: list[StreamOffer] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class NewCampaign:
    name: str
    alias: str
    domain_id: int
    group_id: int
    traffic_source_id: int


@dataclass(frozen=True, slots=True)
class NewGeoRedirectStream:
    campaign_id: int
    name: str
    position: int
    countries: list[str]
    redirect_url: str


@dataclass(frozen=True, slots=True)
class NewOffersStream:
    campaign_id: int
    name: str
    position: int
    offers: list[StreamOffer]


class TrackerProvider(Protocol):
    async def list_domains(self) -> list[NamedRef]: ...

    async def list_campaign_groups(self) -> list[NamedRef]: ...

    async def list_traffic_sources(self) -> list[NamedRef]: ...

    async def search_offers(self, query: str, limit: int) -> list[Offer]: ...

    async def get_offers(self, offer_ids: Sequence[int]) -> list[Offer]: ...

    async def list_campaigns(self) -> list[Campaign]: ...

    async def get_campaign(self, campaign_id: int) -> Campaign: ...

    async def create_campaign(self, campaign: NewCampaign) -> Campaign: ...

    async def archive_campaign(self, campaign_id: int) -> None: ...

    async def list_streams(self, campaign_id: int) -> list[Stream]: ...

    async def create_geo_redirect_stream(self, stream: NewGeoRedirectStream) -> Stream: ...

    async def create_offers_stream(self, stream: NewOffersStream) -> Stream: ...

    async def replace_stream_offers(
        self, stream_id: int, offers: Sequence[StreamOffer]
    ) -> Stream: ...

    def campaign_admin_url(self, campaign_id: int) -> str: ...
