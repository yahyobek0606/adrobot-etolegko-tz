"""create campaign offers

Revision ID: 8b1da24c5d6a
Revises:
Create Date: 2026-11-17 10:13:21.854790
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "8b1da24c5d6a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "campaign_offers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campaign_id", sa.Integer(), nullable=False),
        sa.Column("offer_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("share", sa.Integer(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campaign_offers")),
        sa.UniqueConstraint("campaign_id", "offer_id", name=op.f("uq_campaign_offers_campaign_id")),
    )
    op.create_index(
        op.f("ix_campaign_offers_campaign_id"), "campaign_offers", ["campaign_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_campaign_offers_campaign_id"), table_name="campaign_offers")
    op.drop_table("campaign_offers")
