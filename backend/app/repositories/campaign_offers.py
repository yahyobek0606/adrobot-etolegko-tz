from collections.abc import Sequence
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CampaignOfferRecord
from app.domain.campaign_offers import CampaignOffer


class CampaignOfferRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_for_campaign(self, campaign_id: int) -> list[CampaignOffer]:
        rows = await self._session.scalars(
            select(CampaignOfferRecord)
            .where(CampaignOfferRecord.campaign_id == campaign_id)
            .order_by(CampaignOfferRecord.position)
        )
        return [
            CampaignOffer(
                offer_id=row.offer_id,
                name=row.name,
                share=row.share,
                is_pinned=row.is_pinned,
                is_archived=row.archived_at is not None,
            )
            for row in rows
        ]

    async def replace_for_campaign(self, campaign_id: int, offers: Sequence[CampaignOffer]) -> None:
        existing = {
            row.offer_id: row
            for row in await self._session.scalars(
                select(CampaignOfferRecord).where(CampaignOfferRecord.campaign_id == campaign_id)
            )
        }
        now = datetime.now(UTC)
        wanted = {offer.offer_id for offer in offers}

        stale = [offer_id for offer_id in existing if offer_id not in wanted]
        if stale:
            await self._session.execute(
                delete(CampaignOfferRecord).where(
                    CampaignOfferRecord.campaign_id == campaign_id,
                    CampaignOfferRecord.offer_id.in_(stale),
                )
            )

        for position, offer in enumerate(offers):
            row = existing.get(offer.offer_id)
            if row is None:
                row = CampaignOfferRecord(campaign_id=campaign_id, offer_id=offer.offer_id)
                self._session.add(row)
            row.name = offer.name
            row.share = offer.share
            row.is_pinned = offer.is_pinned
            row.position = position
            if offer.is_archived:
                row.archived_at = row.archived_at or now
            else:
                row.archived_at = None
