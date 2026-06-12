"""Ground-truth tests: parsing each course's real Spring 2026 schedule
must produce EXACTLY the events in 4-CALENDAR-SPEC.md (78 across 4 sites).

Fixtures are rendered from each course repo's actual _modules data
through its actual module layout, so they match the live sites' markup.
"""

from datetime import date
from pathlib import Path

import pytest

from dscal.models import is_deadline
from dscal.parser import parse_events

FIXTURES = Path(__file__).parent / "fixtures"

DSC80 = [
    (4, 8, "LAB 1"),
    (4, 10, "PROJ 1"),
    (4, 15, "LAB 2"),
    (4, 17, "PROJ 1"),
    (4, 22, "LAB 3"),
    (4, 24, "PROJ 2"),
    (4, 29, "LAB 4"),
    (5, 1, "PROJ 2"),
    (5, 5, "EXAM"),
    (5, 6, "LAB 5"),
    (5, 8, "PROJ 3"),
    (5, 13, "LAB 6"),
    (5, 15, "PROJ 3"),
    (5, 20, "LAB 7"),
    (5, 22, "FINAL PROJ"),
    (5, 27, "LAB 8"),
    (5, 29, "FINAL PROJ"),
    (6, 3, "LAB 9"),
    (6, 5, "FINAL PROJ"),
    (6, 9, "EXAM"),
]

DSC106 = [
    (4, 3, "LAB 1"),
    (4, 7, "PROJ 1"),
    (4, 10, "LAB 2"),
    (4, 14, "PROJ 1"),
    (4, 17, "LAB 3"),
    (4, 21, "PROJ 2"),
    (4, 24, "LAB 4"),
    (4, 28, "PROJ 2"),
    (5, 1, "LAB 5"),
    (5, 5, "PROJ 3"),
    (5, 5, "PROJ 2"),
    (5, 8, "LAB 6"),
    (5, 12, "PROJ 3"),
    (5, 15, "LAB 7"),
    (5, 19, "PROJ 3"),
    (5, 19, "FINAL PROJ"),
    (5, 22, "LAB 8"),
    (5, 26, "FINAL PROJ"),
    (6, 2, "FINAL PROJ"),
    (6, 9, "FINAL PROJ"),
]

DSC10 = [
    (4, 6, "LAB 0"),
    (4, 9, "LAB 1"),
    (4, 13, "HW 1"),
    (4, 15, "QUIZ 1"),
    (4, 16, "LAB 2"),
    (4, 20, "HW 2"),
    (4, 22, "QUIZ 2"),
    (4, 23, "LAB 3"),
    (4, 27, "HW 3"),
    (5, 1, "EXAM"),
    (5, 5, "PROJ"),
    (5, 7, "LAB 4"),
    (5, 11, "HW 4"),
    (5, 14, "LAB 5"),
    (5, 18, "HW 5"),
    (5, 20, "QUIZ 3"),
    (5, 21, "LAB 6"),
    (5, 25, "HW 6"),
    (5, 27, "QUIZ 4"),
    (6, 1, "LAB 7"),
    (6, 3, "PROJ"),
    (6, 6, "EXAM"),
]

DSC152 = [
    (4, 6, "LAB 1"),
    (4, 13, "LAB 2"),
    (4, 16, "HW 1"),
    (4, 20, "LAB 3"),
    (4, 22, "QUIZ 1"),
    (4, 27, "LAB 4"),
    (5, 4, "LAB 5"),
    (5, 7, "HW 2"),
    (5, 11, "LAB 6"),
    (5, 13, "QUIZ 2"),
    (5, 18, "LAB 7"),
    (5, 25, "LAB 8"),
    (5, 28, "HW 3"),
    (6, 1, "LAB 9"),
    (6, 3, "QUIZ 3"),
    (6, 6, "EXAM"),
]

CASES = [
    # dsc80_live.html is the REAL page as fetched from dsc80.com
    # (captured 2026-06-11); the *_real.html fixtures are rendered from
    # each course repo's actual schedule data.
    ("dsc80_live.html", "DSC 80", DSC80),
    ("dsc80_real.html", "DSC 80", DSC80),
    ("dsc106_real.html", "DSC 106", DSC106),
    ("dsc10_real.html", "DSC 10", DSC10),
    ("dsc152_real.html", "DSC 152", DSC152),
]


def deadlines(fixture: str, course: str) -> set[tuple[date, str]]:
    html = (FIXTURES / fixture).read_text(encoding="utf-8")
    events = parse_events(html, course=course)
    return {(e.date, e.label) for e in events if is_deadline(e.label)}


@pytest.mark.parametrize("fixture,course,spec", CASES)
def test_exact_spec_match(
    fixture: str, course: str, spec: list[tuple[int, int, str]]
) -> None:
    expected = {(date(2026, m, d), label) for m, d, label in spec}
    got = deadlines(fixture, course)
    missing = sorted(expected - got)
    extra = sorted(got - expected)
    assert got == expected, f"missing={missing} extra={extra}"


def test_total_count() -> None:
    total = sum(len(deadlines(f, c)) for f, c, _ in CASES)
    assert total == 98  # 78 unique + DSC 80 counted twice (live + rendered)
