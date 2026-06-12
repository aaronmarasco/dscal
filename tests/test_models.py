from datetime import date

from dscal.models import Event, Kind, events_in_window


def ev(d: date, label: str = "LAB 1") -> Event:
    return Event(date=d, course="DSC 80", label=label, title="x", kind=Kind.LAB)


def test_window_includes_start_excludes_end() -> None:
    events = [ev(date(2026, 6, 10)), ev(date(2026, 6, 16)), ev(date(2026, 6, 17))]
    got = events_in_window(events, start=date(2026, 6, 10), days=7)
    assert [e.date for e in got] == [date(2026, 6, 10), date(2026, 6, 16)]


def test_window_sorted() -> None:
    events = [ev(date(2026, 6, 12)), ev(date(2026, 6, 11))]
    got = events_in_window(events, start=date(2026, 6, 10), days=7)
    assert [e.date for e in got] == [date(2026, 6, 11), date(2026, 6, 12)]


def test_is_deadline() -> None:
    assert Kind.PROJECT.is_deadline
    assert Kind.EXAM.is_deadline
    assert not Kind.LECTURE.is_deadline
