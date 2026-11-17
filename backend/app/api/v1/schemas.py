from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from app.domain.countries import is_country_code
from app.providers.base import NamedRef, Offer
from app.services.campaign_catalog import CampaignFormOptions, CampaignSummary
from app.services.campaign_offers import CampaignOffersState


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class NamedRefResponse(ApiModel):
    id: int
    name: str

    @classmethod
    def from_ref(cls, ref: NamedRef) -> "NamedRefResponse":
        return cls(id=ref.id, name=ref.name)


class CampaignDefaultsResponse(ApiModel):
    domain_id: int
    group_id: int
    traffic_source_id: int


class CampaignFormOptionsResponse(ApiModel):
    domains: list[NamedRefResponse]
    groups: list[NamedRefResponse]
    traffic_sources: list[NamedRefResponse]
    defaults: CampaignDefaultsResponse
    fallback_redirect_url: str

    @classmethod
    def from_options(cls, options: CampaignFormOptions) -> "CampaignFormOptionsResponse":
        return cls(
            domains=[NamedRefResponse.from_ref(ref) for ref in options.domains],
            groups=[NamedRefResponse.from_ref(ref) for ref in options.groups],
            traffic_sources=[NamedRefResponse.from_ref(ref) for ref in options.traffic_sources],
            defaults=CampaignDefaultsResponse.model_validate(options.defaults),
            fallback_redirect_url=options.fallback_redirect_url,
        )


class OfferResponse(ApiModel):
    id: int
    name: str
    group: str | None
    countries: list[str]

    @classmethod
    def from_offer(cls, offer: Offer) -> "OfferResponse":
        return cls(id=offer.id, name=offer.name, group=offer.group, countries=offer.countries)


class CampaignResponse(ApiModel):
    id: int
    name: str
    alias: str
    is_active: bool
    tracking_url: str
    admin_url: str
    group_id: int | None

    @classmethod
    def from_summary(cls, summary: CampaignSummary) -> "CampaignResponse":
        campaign = summary.campaign
        return cls(
            id=campaign.id,
            name=campaign.name,
            alias=campaign.alias,
            is_active=campaign.is_active,
            tracking_url=campaign.tracking_url,
            admin_url=summary.admin_url,
            group_id=campaign.group_id,
        )


class CampaignCreateRequest(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    countries: Annotated[list[str], Field(min_length=1, max_length=50)]
    offer_id: Annotated[int, Field(gt=0)]
    domain_id: Annotated[int, Field(gt=0)]
    group_id: Annotated[int, Field(gt=0)]
    traffic_source_id: Annotated[int, Field(gt=0)]

    @field_validator("countries")
    @classmethod
    def normalize_countries(cls, countries: list[str]) -> list[str]:
        normalized = list(dict.fromkeys(code.strip().upper() for code in countries))
        invalid = [code for code in normalized if not is_country_code(code)]
        if invalid:
            raise ValueError(f"Invalid ISO 3166-1 alpha-2 country codes: {', '.join(invalid)}")
        return normalized


class StreamResponse(ApiModel):
    id: int
    name: str


class CampaignOfferResponse(ApiModel):
    offer_id: int
    name: str
    share: int
    is_pinned: bool
    is_archived: bool


class CampaignOffersResponse(ApiModel):
    campaign: CampaignResponse
    stream: StreamResponse | None
    offers: list[CampaignOfferResponse]

    @classmethod
    def from_state(cls, state: CampaignOffersState) -> "CampaignOffersResponse":
        return cls(
            campaign=CampaignResponse.from_summary(state.campaign),
            stream=StreamResponse(id=state.stream.id, name=state.stream.name)
            if state.stream
            else None,
            offers=[CampaignOfferResponse.model_validate(offer) for offer in state.offers],
        )


class CampaignOfferInput(BaseModel):
    offer_id: Annotated[int, Field(gt=0)]
    share: Annotated[int, Field(ge=0, le=100)]
    is_pinned: bool
    is_archived: bool


class CampaignOffersUpdateRequest(BaseModel):
    offers: Annotated[list[CampaignOfferInput], Field(max_length=200)]
