import json
from pathlib import Path
from typing import Any

import pytest

from app.domain.shares import ShareError, ShareSlot, allocate_shares

CASES_PATH = Path(__file__).resolve().parents[3] / "shared" / "share-cases.json"
CASES: list[dict[str, Any]] = json.loads(CASES_PATH.read_text())


@pytest.mark.parametrize("case", CASES, ids=[case["name"] for case in CASES])
def test_allocate_shares_matches_shared_cases(case: dict[str, Any]) -> None:
    slots = [ShareSlot(pinned=item["pinned"], share=item["share"]) for item in case["input"]]

    allocation = allocate_shares(slots)

    assert allocation.shares == case["expected"]["shares"]
    expected_error = case["expected"]["error"]
    assert allocation.error == (ShareError(expected_error) if expected_error else None)


def test_valid_allocation_always_sums_to_total() -> None:
    for count in range(1, 30):
        allocation = allocate_shares([ShareSlot(pinned=False, share=0)] * count)

        assert allocation.is_valid
        assert sum(allocation.shares) == 100
        assert max(allocation.shares) - min(allocation.shares) <= 1
