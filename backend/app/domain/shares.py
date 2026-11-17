from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

TOTAL_SHARE = 100


class ShareError(StrEnum):
    NO_ACTIVE_OFFERS = "no_active_offers"
    PINNED_EXCEEDS_TOTAL = "pinned_exceeds_total"
    PINNED_TOTAL_MISMATCH = "pinned_total_mismatch"


@dataclass(frozen=True, slots=True)
class ShareSlot:
    pinned: bool
    share: int


@dataclass(frozen=True, slots=True)
class ShareAllocation:
    shares: list[int]
    error: ShareError | None

    @property
    def is_valid(self) -> bool:
        return self.error is None


def allocate_shares(slots: Sequence[ShareSlot]) -> ShareAllocation:
    if not slots:
        return ShareAllocation(shares=[], error=ShareError.NO_ACTIVE_OFFERS)

    pinned_total = sum(slot.share for slot in slots if slot.pinned)
    unpinned_count = sum(1 for slot in slots if not slot.pinned)
    remainder = TOTAL_SHARE - pinned_total

    if remainder < 0:
        return ShareAllocation(
            shares=[slot.share if slot.pinned else 0 for slot in slots],
            error=ShareError.PINNED_EXCEEDS_TOTAL,
        )

    if unpinned_count == 0:
        error = None if remainder == 0 else ShareError.PINNED_TOTAL_MISMATCH
        return ShareAllocation(shares=[slot.share for slot in slots], error=error)

    base, leftover = divmod(remainder, unpinned_count)
    shares: list[int] = []
    unpinned_index = 0
    for slot in slots:
        if slot.pinned:
            shares.append(slot.share)
            continue
        shares.append(base + (1 if unpinned_index < leftover else 0))
        unpinned_index += 1

    return ShareAllocation(shares=shares, error=None)
