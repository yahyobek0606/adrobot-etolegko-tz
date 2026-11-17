from datetime import datetime

from sqlalchemy import DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class CampaignOfferRecord(TimestampMixin, Base):
    __tablename__ = "campaign_offers"
    __table_args__ = (UniqueConstraint("campaign_id", "offer_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    campaign_id: Mapped[int] = mapped_column(Integer, index=True)
    offer_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(500))
    share: Mapped[int] = mapped_column(Integer)
    is_pinned: Mapped[bool]
    position: Mapped[int] = mapped_column(Integer)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


__all__ = ["Base", "CampaignOfferRecord"]
