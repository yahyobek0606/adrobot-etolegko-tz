import hashlib
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace

from app.domain.errors import InvalidOperationError
from app.domain.shares import ShareError, ShareSlot, allocate_shares

SHARE_ERROR_MESSAGES = {
    ShareError.NO_ACTIVE_OFFERS: "The campaign needs at least one active offer",
    ShareError.PINNED_EXCEEDS_TOTAL: "Pinned shares add up to more than 100%",
    ShareError.PINNED_TOTAL_MISMATCH: "All offers are pinned, so their shares must add up to 100%",
}


@dataclass(frozen=True, slots=True)
class CampaignOffer:
    offer_id: int
    name: str
    share: int
    is_pinned: bool
    is_archived: bool


@dataclass(frozen=True, slots=True)
class RemoteOffer:
    offer_id: int
    share: int


def offers_revision(offers: Iterable[RemoteOffer]) -> str:
    canonical = ",".join(
        f"{o.offer_id}:{o.share}" for o in sorted(offers, key=lambda o: o.offer_id)
    )
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


def active_as_remote(offers: Iterable[CampaignOffer]) -> list[RemoteOffer]:
    return [RemoteOffer(o.offer_id, o.share) for o in offers if not o.is_archived]


def apply_allocation(offers: Sequence[CampaignOffer]) -> list[CampaignOffer]:
    _ensure_unique(offers)
    active = [offer for offer in offers if not offer.is_archived]
    allocation = allocate_shares([ShareSlot(o.is_pinned, o.share) for o in active])
    if allocation.error is not None:
        raise InvalidOperationError(SHARE_ERROR_MESSAGES[allocation.error])

    shares = iter(allocation.shares)
    return [offer if offer.is_archived else replace(offer, share=next(shares)) for offer in offers]


def reconcile(
    local: Sequence[CampaignOffer],
    remote: Sequence[RemoteOffer],
    names: Mapping[int, str],
) -> list[CampaignOffer]:
    local_by_id = {offer.offer_id: offer for offer in local}
    remote_ids = {offer.offer_id for offer in remote}

    active = [
        _from_remote(remote_offer, local_by_id.get(remote_offer.offer_id), names)
        for remote_offer in remote
    ]
    archived = [
        replace(offer, is_archived=True, is_pinned=False)
        for offer in local
        if offer.offer_id not in remote_ids
    ]
    return _pin_if_not_reproducible(active) + archived


def _pin_if_not_reproducible(active: list[CampaignOffer]) -> list[CampaignOffer]:
    allocation = allocate_shares([ShareSlot(o.is_pinned, o.share) for o in active])
    if allocation.shares == [offer.share for offer in active]:
        return active
    return [replace(offer, is_pinned=True) for offer in active]


def _from_remote(
    remote: RemoteOffer, existing: CampaignOffer | None, names: Mapping[int, str]
) -> CampaignOffer:
    fallback_name = existing.name if existing else f"Offer {remote.offer_id}"
    return CampaignOffer(
        offer_id=remote.offer_id,
        name=names.get(remote.offer_id, fallback_name),
        share=remote.share,
        is_pinned=bool(existing and existing.is_pinned and not existing.is_archived),
        is_archived=False,
    )


def _ensure_unique(offers: Sequence[CampaignOffer]) -> None:
    seen: set[int] = set()
    for offer in offers:
        if offer.offer_id in seen:
            raise InvalidOperationError(f"Offer {offer.offer_id} is listed more than once")
        seen.add(offer.offer_id)
