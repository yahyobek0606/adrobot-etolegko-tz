import re
import secrets
import unicodedata
from collections.abc import Callable

MAX_SLUG_LENGTH = 40
FALLBACK_SLUG = "campaign"


def slugify(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_value.lower()).strip("-")
    return slug[:MAX_SLUG_LENGTH].rstrip("-") or FALLBACK_SLUG


def make_alias(name: str, suffix_factory: Callable[[], str] = lambda: secrets.token_hex(3)) -> str:
    return f"{slugify(name)}-{suffix_factory()}"
