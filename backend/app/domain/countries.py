import pycountry

COUNTRY_CODES: frozenset[str] = frozenset(country.alpha_2 for country in pycountry.countries)


def is_country_code(code: str) -> bool:
    return code in COUNTRY_CODES
