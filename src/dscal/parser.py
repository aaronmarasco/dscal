"""HTML -> events. Pure functions; no network access.

Most DSC course sites use the "just-the-class" Jekyll template, which
renders the schedule as:

    <div class="module">
      <h3 class="module-header">Week 3 - ...</h3>
      <dl class="module-days">
        <dt class="module-day main">Tue Apr 14</dt>
        <dd class="module-event main">
          <p class="module-event-type">
            <strong class="label label-lecture">LEC 5</strong>
          </p>
          <div class="module-event-content">
            <p class="module-event-content--title"><a href="...">Title</a></p>
            ...

The event type is carried in the label-* CSS class. For sites not using
this template, a heuristic fallback scans for date patterns near
assignment keywords.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from dscal.dates import extract_quarter, parse_day_label
from dscal.models import Event, Kind

# just-the-class label-* classes -> Kind
LABEL_CLASSES: dict[str, Kind] = {
    "lecture": Kind.LECTURE,
    "lec": Kind.LECTURE,
    "disc": Kind.DISCUSSION,
    "discussion": Kind.DISCUSSION,
    "lab": Kind.LAB,
    "proj": Kind.PROJECT,
    "project": Kind.PROJECT,
    "hw": Kind.HOMEWORK,
    "homework": Kind.HOMEWORK,
    "exam": Kind.EXAM,
}

# Fallback: keywords in an event label -> Kind
_KEYWORD_KINDS: list[tuple[re.Pattern[str], Kind]] = [
    (re.compile(r"\b(lab)\b", re.I), Kind.LAB),
    (re.compile(r"\b(proj|project)\b", re.I), Kind.PROJECT),
    (re.compile(r"\b(hw|homework)\b", re.I), Kind.HOMEWORK),
    (re.compile(r"\b(exam|midterm|final)\b", re.I), Kind.EXAM),
    (re.compile(r"\b(disc|discussion)\b", re.I), Kind.DISCUSSION),
    (re.compile(r"\b(lec|lecture)\b", re.I), Kind.LECTURE),
]


class ParseError(Exception):
    """Raised when a page cannot be parsed at all."""


def parse_events(html: str, course: str) -> list[Event]:
    """Parse a course site's HTML into events.

    Tries the just-the-class template parser first; if it finds nothing,
    falls back to the heuristic parser. Raises ParseError if the page's
    quarter/year cannot be determined.
    """
    quarter = extract_quarter(html)
    if quarter is None:
        raise ParseError(
            f"{course}: could not find a quarter like 'Spring 2026' on the "
            "page, so dates cannot be resolved."
        )
    _, year = quarter
    events = parse_just_the_class(html, course, year)
    if not events:
        events = parse_fallback(html, course, year)
    return events


def _classify(css_classes: list[str], label_text: str) -> Kind:
    for cls in css_classes:
        if cls.startswith("label-"):
            kind = LABEL_CLASSES.get(cls.removeprefix("label-"))
            if kind is not None:
                return kind
    return _classify_keywords(label_text)


def _classify_keywords(text: str) -> Kind:
    for pattern, kind in _KEYWORD_KINDS:
        if pattern.search(text):
            return kind
    return Kind.OTHER


def _event_url(dd: Tag) -> str | None:
    """Best link for an event: the title link, else the first content link."""
    title = dd.select_one(".module-event-content--title a[href]")
    if isinstance(title, Tag):
        return str(title["href"])
    link = dd.select_one(".module-event-content a[href]")
    if isinstance(link, Tag):
        return str(link["href"])
    return None


def parse_just_the_class(html: str, course: str, year: int) -> list[Event]:
    """Parse the just-the-class module/schedule structure."""
    soup = BeautifulSoup(html, "html.parser")
    events: list[Event] = []
    for dl in soup.select("dl.module-days"):
        current = None
        for child in dl.find_all(["dt", "dd"], recursive=False):
            if not isinstance(child, Tag):
                continue
            if child.name == "dt":
                current = parse_day_label(child.get_text(strip=True), year)
                continue
            if current is None:
                continue
            label_el = child.select_one(".module-event-type .label")
            title_el = child.select_one(".module-event-content--title")
            label = label_el.get_text(strip=True) if label_el else ""
            title = " ".join(title_el.get_text(strip=True).split()) if title_el else ""
            if not label and not title:
                continue
            classes = label_el.get("class") if label_el else None
            kind = _classify(
                [str(c) for c in classes] if classes else [], label or title
            )
            events.append(
                Event(
                    date=current,
                    course=course,
                    label=label,
                    title=title,
                    kind=kind,
                    url=_event_url(child),
                )
            )
    return events


_FALLBACK_DATE_RE = re.compile(
    r"\b(?:mon|tue|wed|thu|fri|sat|sun)?[a-z]*\.?,?\s*"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+"
    r"(\d{1,2})\b",
    re.IGNORECASE,
)

_FALLBACK_KEYWORD_RE = re.compile(
    r"\b(lab|proj|project|hw|homework|exam|midterm|final|due|checkpoint|"
    r"quiz)\b",
    re.IGNORECASE,
)


def parse_fallback(html: str, course: str, year: int) -> list[Event]:
    """Heuristic parser for non-template sites.

    Scans table rows and list items for a date pattern; rows that also
    mention an assignment keyword become deadline events. Best-effort by
    design: misses are reported by the CLI, not silently ignored.
    """
    soup = BeautifulSoup(html, "html.parser")
    events: list[Event] = []
    seen: set[tuple[str, str]] = set()
    for el in soup.find_all(["tr", "li", "p", "dd"]):
        if not isinstance(el, Tag):
            continue
        text = " ".join(el.get_text(" ", strip=True).split())
        if len(text) > 300:
            continue
        m = _FALLBACK_DATE_RE.search(text)
        kw = _FALLBACK_KEYWORD_RE.search(text)
        if m is None or kw is None:
            continue
        d = parse_day_label(f"{m.group(1)} {m.group(2)}", year)
        if d is None:
            continue
        key = (text, str(d))
        if key in seen:
            continue
        seen.add(key)
        link = el.find("a", href=True)
        events.append(
            Event(
                date=d,
                course=course,
                label=kw.group(1).upper(),
                title=text[:120],
                kind=_classify_keywords(text),
                url=str(link["href"]) if isinstance(link, Tag) else None,
            )
        )
    return events
