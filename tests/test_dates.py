from datetime import date

from dscal.dates import extract_quarter, in_quarter, parse_day_label


def test_extract_quarter_from_meta_text(dsc80_html: str) -> None:
    assert extract_quarter(dsc80_html) == ("spring", 2026)


def test_extract_quarter_plain() -> None:
    assert extract_quarter("DSC 10, Fall 2025 at UC San Diego") == ("fall", 2025)


def test_extract_quarter_case_insensitive() -> None:
    assert extract_quarter("winter 2026 offering") == ("winter", 2026)


def test_extract_quarter_missing() -> None:
    assert extract_quarter("no quarter mentioned here") is None


def test_parse_day_label_simple() -> None:
    assert parse_day_label("Tue Apr 14", 2026) == date(2026, 4, 14)


def test_parse_day_label_double_space() -> None:
    # Jekyll's %e directive space-pads single-digit days: "Wed Apr  8"
    assert parse_day_label("Wed Apr  8", 2026) == date(2026, 4, 8)


def test_parse_day_label_no_weekday() -> None:
    assert parse_day_label("Apr 14", 2026) == date(2026, 4, 14)


def test_parse_day_label_not_a_date() -> None:
    assert parse_day_label("Office Hours", 2026) is None


def test_in_quarter() -> None:
    assert in_quarter(date(2026, 4, 14), "spring", 2026)
    assert not in_quarter(date(2026, 12, 25), "spring", 2026)
    assert not in_quarter(date(2025, 4, 14), "spring", 2026)
