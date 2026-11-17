import re

import pytest

from app.domain.alias import make_alias, slugify


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("My Campaign", "my-campaign"),
        ("  test__AU  geo!! ", "test-au-geo"),
        ("Café déjà vu", "cafe-deja-vu"),
        ("тест_орлов", "campaign"),
        ("x" * 60, "x" * 40),
    ],
)
def test_slugify(name: str, expected: str) -> None:
    assert slugify(name) == expected


def test_make_alias_appends_random_suffix() -> None:
    first, second = make_alias("My Campaign"), make_alias("My Campaign")

    assert re.fullmatch(r"my-campaign-[0-9a-f]{6}", first)
    assert first != second
