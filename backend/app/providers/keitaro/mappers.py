from app.providers.base import (
    Campaign,
    NamedRef,
    Offer,
    Stream,
    StreamKind,
    StreamOffer,
)
from app.providers.keitaro.schemas import (
    KeitaroCampaign,
    KeitaroNamed,
    KeitaroOffer,
    KeitaroStream,
)

ACTIVE = "active"
COUNTRY_FILTER = "country"
LANDINGS_SCHEMA = "landings"
REDIRECT_SCHEMA = "redirect"


def to_named_ref(raw: KeitaroNamed) -> NamedRef:
    return NamedRef(id=raw.id, name=raw.name)


def to_offer(raw: KeitaroOffer) -> Offer:
    return Offer(
        id=raw.id,
        name=raw.name,
        group=raw.group or None,
        countries=raw.country,
        is_active=raw.state == ACTIVE,
    )


def to_campaign(raw: KeitaroCampaign) -> Campaign:
    domain = raw.domain or ""
    if domain and not domain.endswith("/"):
        domain += "/"
    return Campaign(
        id=raw.id,
        name=raw.name,
        alias=raw.alias,
        is_active=raw.state == ACTIVE,
        tracking_url=f"{domain}{raw.alias}" if domain else raw.alias,
        domain_id=raw.domain_id,
        group_id=raw.group_id,
        traffic_source_id=raw.traffic_source_id,
    )


def _countries(raw: KeitaroStream) -> list[str]:
    for stream_filter in raw.filters:
        if stream_filter.name == COUNTRY_FILTER and isinstance(stream_filter.payload, list):
            return stream_filter.payload
    return []


def _kind(raw: KeitaroStream, countries: list[str]) -> StreamKind:
    if raw.schema_ == LANDINGS_SCHEMA:
        return StreamKind.OFFERS
    if raw.schema_ == REDIRECT_SCHEMA and countries:
        return StreamKind.GEO_REDIRECT
    return StreamKind.OTHER


def to_stream(raw: KeitaroStream) -> Stream:
    countries = _countries(raw)
    return Stream(
        id=raw.id,
        campaign_id=raw.campaign_id,
        name=raw.name,
        position=raw.position,
        kind=_kind(raw, countries),
        countries=countries,
        redirect_url=raw.action_payload or None,
        offers=[
            StreamOffer(offer_id=offer.offer_id, share=offer.share, is_active=offer.state == ACTIVE)
            for offer in raw.offers
        ],
    )


def stream_offers_payload(offers: list[StreamOffer]) -> list[dict[str, object]]:
    return [
        {
            "offer_id": offer.offer_id,
            "share": offer.share,
            "state": ACTIVE if offer.is_active else "disabled",
        }
        for offer in offers
    ]
