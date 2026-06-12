from datetime import date

from dscal.ics import to_ics
from dscal.models import Event, Kind


def make_event() -> Event:
    return Event(
        date=date(2026, 4, 17),
        course="DSC 80",
        label="PROJ 1",
        kind=Kind.PROJECT,
    )


def test_calendar_structure() -> None:
    text = to_ics([make_event()])
    assert text.startswith("BEGIN:VCALENDAR")
    assert text.rstrip().endswith("END:VCALENDAR")
    assert text.count("BEGIN:VEVENT") == 1


def test_all_day_event() -> None:
    text = to_ics([make_event()])
    assert "DTSTART;VALUE=DATE:20260417" in text
    assert "DTEND;VALUE=DATE:20260418" in text


def test_summary_is_bare_label() -> None:
    text = to_ics([make_event()])
    assert "SUMMARY:DSC 80: PROJ 1" in text
    assert "URL:" not in text
    assert "DESCRIPTION:" not in text


def test_deterministic_uid() -> None:
    a = to_ics([make_event()])
    b = to_ics([make_event()])
    uid_a = [ln for ln in a.splitlines() if ln.startswith("UID:")]
    assert uid_a and uid_a == [ln for ln in b.splitlines() if ln.startswith("UID:")]


def test_crlf_line_endings() -> None:
    text = to_ics([make_event()])
    assert "\r\n" in text
