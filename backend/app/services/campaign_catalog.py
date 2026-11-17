import asyncio
from dataclasses import dataclass

from app.providers.base import Campaign, NamedRef, Offer, TrackerProvider


@dataclass(frozen=True, slots=True)
class CampaignDefaults:
    domain_id: int
    group_id: int
    traffic_source_id: int


@dataclass(frozen=True, slots=True)
class CampaignFormOptions:
    domains: list[NamedRef]
    groups: list[NamedRef]
    traffic_sources: list[NamedRef]
    defaults: CampaignDefaults
    fallback_redirect_url: str


@dataclass(frozen=True, slots=True)
class CampaignSummary:
    campaign: Campaign
    admin_url: str


class CampaignCatalogService:
    def __init__(
        self,
        provider: TrackerProvider,
        defaults: CampaignDefaults,
        fallback_redirect_url: str,
    ) -> None:
        self._provider = provider
        self._defaults = defaults
        self._fallback_redirect_url = fallback_redirect_url

    async def list_campaigns(self) -> list[CampaignSummary]:
        campaigns = await self._provider.list_campaigns()
        return [self.summarize(campaign) for campaign in campaigns]

    async def form_options(self) -> CampaignFormOptions:
        domains, groups, traffic_sources = await asyncio.gather(
            self._provider.list_domains(),
            self._provider.list_campaign_groups(),
            self._provider.list_traffic_sources(),
        )
        return CampaignFormOptions(
            domains=domains,
            groups=groups,
            traffic_sources=traffic_sources,
            defaults=self._defaults,
            fallback_redirect_url=self._fallback_redirect_url,
        )

    async def search_offers(self, query: str, limit: int) -> list[Offer]:
        return await self._provider.search_offers(query, limit)

    def summarize(self, campaign: Campaign) -> CampaignSummary:
        return CampaignSummary(
            campaign=campaign, admin_url=self._provider.campaign_admin_url(campaign.id)
        )
