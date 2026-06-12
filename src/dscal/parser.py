"""HTML -> events. Pure functions; no network access.

All DSC course sites observed use the "just-the-class" Jekyll template
(in a couple of layout variants), which always renders the schedule as
<dl class="module-days"> lists where:

  - <dt class="module-day">Tue Apr 14</dt> carries the date, and
  - every event is a <strong class="label label-{type}">NAME</strong>
    somewhere below it.

So the parser needs just one rule: walk each dl in document order,
remember the most recent date, and emit one event per label element.
Events on a date-less or unparseable row are skipped. Duplicate
(course, label, date) triples -- e.g. "QUIZ 1" plus its solutions row --
collapse to one event.

For sites not using this template at all, a heuristic fallback scans
rows for a date pattern plus a deliverable label.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from bs4.element import Tag

from dscal.dates import extract_quarter, parse_day_label
from dscal.models import Event, Kind, normalize_label

# just-the-class label-* CSS classes -> Kind (display only)
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
    "quiz": Kind.QUIZ,
    "exam": Kind.EXAM,
}

_KEYWORD_KINDS: list[tuple[re.Pattern[str], Kind]] = [
    (re.compile(r"\bLAB\b"), Kind.LAB),
    (re.compile(r"\b(PROJ|PROJECT)\b"), Kind.PROJECT),
    (re.compile(r"\b(HW|HOMEWORK)\b"), Kind.HOMEWORK),
    (re.compile(r"\bQUIZ\b"), Kind.QUIZ),
    (re.compile(r"\b(EXAM|MIDTERM|FINAL)\b"), Kind.EXAM),
    (re.compile(r"\b(DISC|DISCUSSION)\b"), Kind.DISCUSSION),
    (re.compile(r"\b(LEC|LECTURE)\b"), Kind.LECTURE),
]


class ParseError(Exception):
    """Raised when a page cannot be parsed at all."""


def parse_events(html: str, course: str) -> list[Event]:
    """Parse a course site's HTML into (deduplicated) events.

    Raises ParseError if the page's quarter/year cannot be determined.
    """
    quarter = extract_quarter(html)
    if quarter is None:
        raise ParseError(
            f"{course}: could not find a quarter like 'Spring 2026' on the "
            "page, so dates cannot be resolved."
        )
    _, year = quarter
    soup = BeautifulSoup(html, "html.parser")
    if soup.select("dl.module-days"):
        return parse_just_the_class(soup, course, year)
    return parse_fallback(soup, course, year)


def _classify(css_classes: list[str], label: str) -> Kind:
    for cls in css_classes:
        if cls.startswith("label-"):
            kind = LABEL_CLASSES.get(cls.removeprefix("label-"))
            if kind is not None:
                return kind
    for pattern, kind in _KEYWORD_KINDS:
        if pattern.search(label):
            return kind
    return Kind.OTHER


def parse_just_the_class(soup: BeautifulSoup, course: str, year: int) -> list[Event]:
    """One rule: dt.module-day sets the date; strong.label is an event."""
    events: list[Event] = []
    seen: set[tuple[str, str]] = set()
    for dl in soup.select("dl.module-days"):
        current = None
        for el in dl.find_all(["dt", "strong"]):
            if not isinstance(el, Tag):
                continue
            classes = [str(c) for c in (el.get("class") or [])]
            if el.name == "dt" and "module-day" in classes:
                current = parse_day_label(el.get_text(strip=True), year)
            elif el.name == "strong" and "label" in classes:
                if current is None:
                    continue
                label = normalize_label(el.get_text())
                if not label:
                    continue
                key = (label, current.isoformat())
                if key in seen:
                    continue
                seen.add(key)
                events.append(
                    Event(
                        date=current,
                        course=course,
                        label=label,
                        kind=_classify(classes, label),
                    )
                )
    return events


_FALLBACK_DATE_RE = re.compile(
    r"\b(?:mon|tue|wed|thu|fri|sat|sun)?[a-z]*\.?,?\s*"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+"
    r"(\d{1,2})\b",
    re.IGNORECASE,
)

_FALLBACK_LABEL_RE = re.compile(
    r"\b(FINAL PROJ|LAB|HW|QUIZ|PROJ|EXAM|MIDTERM)\s*(\d+)?\b"
)


def parse_fallback(soup: BeautifulSoup, course: str, year: int) -> list[Event]:
    """Heuristic for non-template sites: a date and a deliverable label
    in the same table row / list item. Best-effort by design."""
    events: list[Event] = []
    seen: set[tuple[str, str]] = set()
    for el in soup.find_all(["tr", "li", "dd", "p"]):
        if not isinstance(el, Tag):
            continue
        text = " ".join(el.get_text(" ", strip=True).split())
        if len(text) > 200:
            continue
        date_m = _FALLBACK_DATE_RE.search(text)
        label_m = _FALLBACK_LABEL_RE.search(normalize_label(text))
        if date_m is None or label_m is None:
            continue
        d = parse_day_label(f"{date_m.group(1)} {date_m.group(2)}", year)
        if d is None:
            continue
        label = label_m.group(0).strip()
        key = (label, d.isoformat())
        if key in seen:
            continue
        seen.add(key)
        events.append(
            Event(
                date=d,
                course=course,
                label=label,
                kind=_classify([], label),
            )
        )
    return events
