from datetime import date

from dscal.models import (
    Event,
    Kind,
    events_in_window,
    is_deadline,
    normalize_label,
)


def ev(d: date, label: str = "LAB 1") -> Event:
    return Event(date=d, course="DSC 80", label=label, kind=Kind.LAB)


def test_window_includes_start_excludes_end() -> None:
    events = [ev(date(2026, 6, 10)), ev(date(2026, 6, 16)), ev(date(2026, 6, 17))]
    got = events_in_window(events, start=date(2026, 6, 10), days=7)
    assert [e.date for e in got] == [date(2026, 6, 10), date(2026, 6, 16)]


def test_window_sorted() -> None:
    events = [ev(date(2026, 6, 12)), ev(date(2026, 6, 11))]
    got = events_in_window(events, start=date(2026, 6, 10), days=7)
    assert [e.date for e in got] == [date(2026, 6, 11), date(2026, 6, 12)]


def test_summary_is_bare() -> None:
    assert ev(date(2026, 6, 12)).summary == "DSC 80: LAB 1"


def test_normalize_label() -> None:
    assert normalize_label("HW1") == "HW 1"
    assert normalize_label("  lab   2 ") == "LAB 2"
    assert normalize_label("Final Proj") == "FINAL PROJ"


def test_is_deadline_accepts_deliverables() -> None:
    for label in [
        "LAB 1",
        "LAB 0",
        "HW 6",
        "QUIZ 4",
        "PROJ",
        "PROJ 3",
        "FINAL PROJ",
        "EXAM",
    ]:
        assert is_deadline(label), label


def test_is_deadline_rejects_everything_else() -> None:
    for label in [
        "LEC 5",
        "DISC 2",
        "REV",
        "BONUS",
        "SUR",
        "SYL",
        "PRE",
        "PRAC",
        "QUIZ 3 SOLUTIONS",
        "DATA",
        "CANCELED",
        "CODE",
    ]:
        assert not is_deadline(label), label
