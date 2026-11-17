import pytest

from app.domain.campaign_offers import (
    CampaignOffer,
    RemoteOffer,
    active_as_remote,
    apply_allocation,
    offers_revision,
    reconcile,
)
from app.domain.errors import InvalidOperationError


def offer(
    offer_id: int,
    share: int = 0,
    *,
    pinned: bool = False,
    archived: bool = False,
    name: str | None = None,
) -> CampaignOffer:
    return CampaignOffer(
        offer_id=offer_id,
        name=name or f"Offer {offer_id}",
        share=share,
        is_pinned=pinned,
        is_archived=archived,
    )


class TestApplyAllocation:
    def test_recomputes_unpinned_and_skips_archived(self) -> None:
        result = apply_allocation(
            [offer(1, 25, pinned=True), offer(2, 99), offer(3, 40, archived=True), offer(4)]
        )

        assert [(o.offer_id, o.share) for o in result] == [(1, 25), (2, 38), (3, 40), (4, 37)]

    @pytest.mark.parametrize(
        ("offers", "message"),
        [
            ([offer(1, archived=True)], "at least one active offer"),
            ([offer(1, 70, pinned=True), offer(2, 40, pinned=True)], "more than 100%"),
            ([offer(1, 50, pinned=True)], "must add up to 100%"),
            ([offer(1), offer(1)], "more than once"),
        ],
    )
    def test_rejects_invalid_drafts(self, offers: list[CampaignOffer], message: str) -> None:
        with pytest.raises(InvalidOperationError, match=message):
            apply_allocation(offers)


class TestReconcile:
    def test_takes_remote_shares_and_keeps_pins(self) -> None:
        local = [offer(1, 60, pinned=True), offer(2, 40)]

        result = reconcile(local, [RemoteOffer(1, 50), RemoteOffer(2, 50)], {})

        assert result == [offer(1, 50, pinned=True), offer(2, 50)]

    def test_archives_offers_removed_in_provider(self) -> None:
        local = [offer(1, 50, pinned=True), offer(2, 50)]

        result = reconcile(local, [RemoteOffer(2, 100)], {})

        assert result == [offer(2, 100), offer(1, 50, archived=True)]

    def test_adds_offers_added_in_provider_and_resolves_names(self) -> None:
        result = reconcile([offer(1, 100)], [RemoteOffer(1, 50), RemoteOffer(7, 50)], {7: "Seven"})

        assert result == [offer(1, 50), offer(7, 50, name="Seven")]

    def test_restores_archived_offer_that_reappears_unpinned(self) -> None:
        local = [offer(1, 100), offer(2, 30, archived=True)]

        result = reconcile(local, [RemoteOffer(1, 50), RemoteOffer(2, 50)], {})

        assert result == [offer(1, 50), offer(2, 50)]

    def test_pins_remote_shares_that_an_even_split_would_change(self) -> None:
        result = reconcile([], [RemoteOffer(1, 33), RemoteOffer(2, 67)], {})

        assert result == [offer(1, 33, pinned=True), offer(2, 67, pinned=True)]

    def test_leaves_even_remote_split_unpinned(self) -> None:
        result = reconcile([], [RemoteOffer(1, 34), RemoteOffer(2, 33), RemoteOffer(3, 33)], {})

        assert [o.is_pinned for o in result] == [False, False, False]

    def test_keeps_previously_archived_offers(self) -> None:
        local = [offer(1, 100), offer(2, 10, archived=True)]

        result = reconcile(local, [RemoteOffer(1, 100)], {})

        assert result == [offer(1, 100), offer(2, 10, archived=True)]


class TestOffersRevision:
    def test_ignores_order(self) -> None:
        assert offers_revision([RemoteOffer(1, 40), RemoteOffer(2, 60)]) == offers_revision(
            [RemoteOffer(2, 60), RemoteOffer(1, 40)]
        )

    def test_changes_with_shares(self) -> None:
        assert offers_revision([RemoteOffer(1, 100)]) != offers_revision([RemoteOffer(1, 99)])

    def test_local_active_offers_match_their_remote_counterpart(self) -> None:
        local = [offer(1, 60), offer(2, 40, pinned=True), offer(3, 10, archived=True)]

        assert offers_revision(active_as_remote(local)) == offers_revision(
            [RemoteOffer(1, 60), RemoteOffer(2, 40)]
        )
