from datetime import date

from dscal.models import Kind
from dscal.parser import parse_events


def test_parses_all_events(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    assert len(events) == 5


def test_event_fields(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    proj = next(e for e in events if e.label == "PROJ 1")
    assert proj.course == "DSC 80"
    assert proj.title == "Project 1"
    assert proj.kind == Kind.PROJECT
    assert proj.date == date(2026, 4, 17)
    assert proj.url is not None and "proj01" in proj.url


def test_single_digit_day(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    lab = next(e for e in events if e.label == "LAB 1")
    assert lab.date == date(2026, 4, 8)


def test_kinds_from_label_classes(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    kinds = {e.label: e.kind for e in events}
    assert kinds["LEC 1"] == Kind.LECTURE
    assert kinds["LAB 1"] == Kind.LAB
    assert kinds["EXAM"] == Kind.EXAM


def test_deadlines_only(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    deadlines = [e for e in events if e.kind.is_deadline]
    assert {e.label for e in deadlines} == {"LAB 1", "PROJ 1", "EXAM"}


def test_title_link_preferred_over_notebook_link(dsc80_html: str) -> None:
    events = parse_events(dsc80_html, course="DSC 80")
    lec1 = next(e for e in events if e.label == "LEC 1")
    assert lec1.url == "https://example.com/lec01"
