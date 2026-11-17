import asyncio
from collections.abc import Sequence
from dataclasses import dataclass

import structlog

from app.db.unit_of_work import UnitOfWork
from app.domain.campaign_offers import (
    CampaignOffer,
    RemoteOffer,
    apply_allocation,
    reconcile,
)
from app.domain.errors import InvalidOperationError, NotFoundError
from app.providers.base import Stream, StreamKind, StreamOffer, TrackerProvider
from app.services.campaign_catalog import CampaignSummary

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True)
class OfferDraft:
    offer_id: int
    share: int
    is_pinned: bool
    is_archived: bool


@dataclass(frozen=True, slots=True)
class CampaignOffersState:
    campaign: CampaignSummary
    stream: Stream | None
    offers: list[CampaignOffer]


class CampaignOffersService:
    def __init__(self, provider: TrackerProvider, uow: UnitOfWork) -> None:
        self._provider = provider
        self._uow = uow

    async def get_state(self, campaign_id: int) -> CampaignOffersState:
        campaign, stream = await self._load_remote(campaign_id)
        offers = await self._uow.campaign_offers.list_for_campaign(campaign_id)
        if not offers and stream is not None and stream.offers:
            offers = await self._store_reconciled(campaign_id, [], stream)
        return CampaignOffersState(campaign=campaign, stream=stream, offers=offers)

    async def sync(self, campaign_id: int) -> CampaignOffersState:
        campaign, stream = await self._load_remote(campaign_id)
        local = await self._uow.campaign_offers.list_for_campaign(campaign_id)
        if stream is None:
            return CampaignOffersState(campaign=campaign, stream=None, offers=local)
        offers = await self._store_reconciled(campaign_id, local, stream)
        logger.info("campaign_offers_synced", campaign_id=campaign_id, offers=len(offers))
        return CampaignOffersState(campaign=campaign, stream=stream, offers=offers)

    async def push(self, campaign_id: int, drafts: Sequence[OfferDraft]) -> CampaignOffersState:
        campaign, stream = await self._load_remote(campaign_id)
        if stream is None:
            raise InvalidOperationError("This campaign has no offers flow to update")

        local = await self._uow.campaign_offers.list_for_campaign(campaign_id)
        names = await self._resolve_names(drafts, {offer.offer_id: offer.name for offer in local})
        offers = apply_allocation(
            [
                CampaignOffer(
                    offer_id=draft.offer_id,
                    name=names[draft.offer_id],
                    share=draft.share,
                    is_pinned=draft.is_pinned and not draft.is_archived,
                    is_archived=draft.is_archived,
                )
                for draft in drafts
            ]
        )

        updated = await self._provider.replace_stream_offers(
            stream.id,
            [StreamOffer(o.offer_id, o.share) for o in offers if not o.is_archived],
        )
        await self._uow.campaign_offers.replace_for_campaign(campaign_id, offers)
        await self._uow.commit()
        logger.info("campaign_offers_pushed", campaign_id=campaign_id, stream_id=stream.id)
        return CampaignOffersState(campaign=campaign, stream=updated, offers=offers)

    async def _load_remote(self, campaign_id: int) -> tuple[CampaignSummary, Stream | None]:
        campaign, streams = await asyncio.gather(
            self._provider.get_campaign(campaign_id),
            self._provider.list_streams(campaign_id),
        )
        stream = next((s for s in streams if s.kind is StreamKind.OFFERS), None)
        summary = CampaignSummary(
            campaign=campaign, admin_url=self._provider.campaign_admin_url(campaign.id)
        )
        return summary, stream

    async def _store_reconciled(
        self, campaign_id: int, local: Sequence[CampaignOffer], stream: Stream
    ) -> list[CampaignOffer]:
        remote = [RemoteOffer(o.offer_id, o.share) for o in stream.offers]
        catalog = await self._provider.get_offers([o.offer_id for o in remote])
        offers = reconcile(local, remote, {offer.id: offer.name for offer in catalog})
        await self._uow.campaign_offers.replace_for_campaign(campaign_id, offers)
        await self._uow.commit()
        return offers

    async def _resolve_names(
        self, drafts: Sequence[OfferDraft], known: dict[int, str]
    ) -> dict[int, str]:
        unknown = [draft.offer_id for draft in drafts if draft.offer_id not in known]
        if not unknown:
            return known
        found = {offer.id: offer.name for offer in await self._provider.get_offers(unknown)}
        missing = [offer_id for offer_id in unknown if offer_id not in found]
        if missing:
            raise NotFoundError(f"Offers not found: {', '.join(map(str, missing))}")
        return {**known, **found}
