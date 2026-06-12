"""Quarter and date inference for course websites.

Course schedule entries render dates like "Tue Apr 14" -- with no year.
But every site states its quarter (e.g. "DSC 80, Spring 2026 at UC San
Diego") in its header/meta description, which pins down the year.
"""

from __future__ import annotations

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


def extract_quarter(page_text: str) -> tuple[str, int] | None:
    """Find a quarter mention like "Spring 2026" in page text.

    Returns (quarter, year), e.g. ("spring", 2026), or None if absent.
    """
    raise NotImplementedError


def parse_day_label(label: str, year: int) -> date | None:
    """Parse a schedule date label like "Tue Apr 14" or "Wed Apr  8".

    Tolerates extra whitespace and a missing weekday. Returns None if the
    label is not a date.
    """
    raise NotImplementedError


def in_quarter(d: date, quarter: str, year: int) -> bool:
    """Sanity check: does this date plausibly fall within the quarter?"""
    lo, hi = QUARTER_MONTHS[quarter]
    return d.year == year and lo <= d.month <= hi
