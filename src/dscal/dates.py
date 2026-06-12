"""Quarter and date inference for course websites.

Course schedule entries render dates like "Tue Apr 14" -- with no year.
But every site states its quarter (e.g. "DSC 80, Spring 2026 at UC San
Diego") in its header/meta description, which pins down the year.
"""

from __future__ import annotations

import re
from datetime import date

QUARTERS = ("winter", "spring", "summer", "fall")

# Months each UCSD quarter can plausibly touch (inclusive ranges).
# Used as a sanity check on parsed dates.
QUARTER_MONTHS: dict[str, tuple[int, int]] = {
    "winter": (1, 4),
    "spring": (3, 6),
    "summer": (6, 9),
    "fall": (9, 12),
}

_QUARTER_RE = re.compile(
    r"\b(winter|spring|summer|fall)\b[\s,]*(\d{4})", re.IGNORECASE
)

_MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

_DAY_LABEL_RE = re.compile(
    r"^(?:(?:mon|tue|wed|thu|fri|sat|sun)[a-z]*\s+)?"
    r"([a-z]{3,9})\.?\s+(\d{1,2})$",
    re.IGNORECASE,
)


def extract_quarter(page_text: str) -> tuple[str, int] | None:
    """Find a quarter mention like "Spring 2026" in page text.

    Returns (quarter, year), e.g. ("spring", 2026), or None if absent.
    """
    m = _QUARTER_RE.search(page_text)
    if m is None:
        return None
    return m.group(1).lower(), int(m.group(2))


def parse_day_label(label: str, year: int) -> date | None:
    """Parse a schedule date label like "Tue Apr 14" or "Wed Apr  8".

    Tolerates extra whitespace and a missing weekday. Returns None if the
    label is not a date.
    """
    cleaned = " ".join(label.split())
    m = _DAY_LABEL_RE.match(cleaned)
    if m is None:
        return None
    month = _MONTHS.get(m.group(1).lower()[:3])
    if month is None:
        return None
    try:
        return date(year, month, int(m.group(2)))
    except ValueError:
        return None


def in_quarter(d: date, quarter: str, year: int) -> bool:
    """Sanity check: does this date plausibly fall within the quarter?"""
    lo, hi = QUARTER_MONTHS[quarter]
    return d.year == year and lo <= d.month <= hi
