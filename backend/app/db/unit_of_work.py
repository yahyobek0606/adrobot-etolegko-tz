from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.campaign_offers import CampaignOfferRepository


class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.campaign_offers = CampaignOfferRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
