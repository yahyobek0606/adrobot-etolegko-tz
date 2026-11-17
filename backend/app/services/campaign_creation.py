from collections.abc import Callable
from dataclasses import dataclass
from urllib.parse import urlsplit

import structlog

from app.domain.alias import make_alias
from app.domain.errors import NotFoundError
from app.domain.shares import TOTAL_SHARE
from app.providers.base import (
    Campaign,
    NewCampaign,
    NewGeoRedirectStream,
    NewOffersStream,
    StreamOffer,
    TrackerProvider,
)

logger = structlog.get_logger()

GEO_STREAM_POSITION = 1
OFFERS_STREAM_POSITION = 2
OFFERS_STREAM_NAME = "Offers"


@dataclass(frozen=True, slots=True)
class CreateCampaignCommand:
    name: str
    countries: list[str]
    offer_id: int
    domain_id: int
    group_id: int
    traffic_source_id: int


class CampaignCreationService:
    def __init__(
        self,
        provider: TrackerProvider,
        fallback_redirect_url: str,
        alias_factory: Callable[[str], str] = make_alias,
    ) -> None:
        self._provider = provider
        self._fallback_redirect_url = fallback_redirect_url
        self._alias_factory = alias_factory

    async def create(self, command: CreateCampaignCommand) -> Campaign:
        await self._ensure_offer_exists(command.offer_id)

        campaign = await self._provider.create_campaign(
            NewCampaign(
                name=command.name,
                alias=self._alias_factory(command.name),
                domain_id=command.domain_id,
                group_id=command.group_id,
                traffic_source_id=command.traffic_source_id,
            )
        )
        try:
            await self._create_streams(campaign.id, command)
        except Exception:
            await self._rollback(campaign.id)
            raise

        logger.info("campaign_created", campaign_id=campaign.id, alias=campaign.alias)
        return campaign

    async def _ensure_offer_exists(self, offer_id: int) -> None:
        if not await self._provider.get_offers([offer_id]):
            raise NotFoundError(f"Offer {offer_id} not found")

    async def _create_streams(self, campaign_id: int, command: CreateCampaignCommand) -> None:
        await self._provider.create_geo_redirect_stream(
            NewGeoRedirectStream(
                campaign_id=campaign_id,
                name=self._geo_stream_name(command.countries),
                position=GEO_STREAM_POSITION,
                countries=command.countries,
                redirect_url=self._fallback_redirect_url,
            )
        )
        await self._provider.create_offers_stream(
            NewOffersStream(
                campaign_id=campaign_id,
                name=OFFERS_STREAM_NAME,
                position=OFFERS_STREAM_POSITION,
                offers=[StreamOffer(offer_id=command.offer_id, share=TOTAL_SHARE)],
            )
        )

    async def _rollback(self, campaign_id: int) -> None:
        logger.warning("campaign_creation_rollback", campaign_id=campaign_id)
        try:
            await self._provider.archive_campaign(campaign_id)
        except Exception:
            logger.exception("campaign_rollback_failed", campaign_id=campaign_id)

    def _geo_stream_name(self, countries: list[str]) -> str:
        host = urlsplit(self._fallback_redirect_url).hostname or self._fallback_redirect_url
        return f"{', '.join(countries)} → {host}"
