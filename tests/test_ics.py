from datetime import date

from dscal.ics import to_ics
from dscal.models import Event, Kind


def make_event() -> Event:
    return Event(
        date=date(2026, 4, 17),
        course="DSC 80",
        label="PROJ 1",
        title="Project 1; with, special chars",
        kind=Kind.PROJECT,
        url="https://example.com/proj1",
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


def test_summary_escaped() -> None:
    text = to_ics([make_event()])
    assert (
        "DSC 80: PROJ 1 \\u2013 Project 1\\; with\\, special chars".replace(
            "\\u2013", "-"
        )
        in text
        or "Project 1\\; with\\, special chars" in text
    )


def test_deterministic_uid() -> None:
    a = to_ics([make_event()])
    b = to_ics([make_event()])
    uid_a = [ln for ln in a.splitlines() if ln.startswith("UID:")]
    assert uid_a and uid_a == [ln for ln in b.splitlines() if ln.startswith("UID:")]


def test_crlf_line_endings() -> None:
    text = to_ics([make_event()])
    assert "\r\n" in text
