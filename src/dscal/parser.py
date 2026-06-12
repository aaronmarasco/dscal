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

from dscal.models import Event

# just-the-class label-* classes -> our Kind values
LABEL_CLASSES: dict[str, str] = {
    "lecture": "lecture",
    "disc": "discussion",
    "discussion": "discussion",
    "lab": "lab",
    "proj": "project",
    "project": "project",
    "hw": "homework",
    "homework": "homework",
    "exam": "exam",
}


def parse_events(html: str, course: str) -> list[Event]:
    """Parse a course site's HTML into events.

    Tries the just-the-class template parser first; if it finds nothing,
    falls back to the heuristic parser. Raises ParseError if the page's
    quarter/year cannot be determined.
    """
    raise NotImplementedError


def parse_just_the_class(html: str, course: str, year: int) -> list[Event]:
    """Parse the just-the-class module/schedule structure."""
    raise NotImplementedError


def parse_fallback(html: str, course: str, year: int) -> list[Event]:
    """Heuristic parser for non-template sites: date patterns near
    assignment keywords."""
    raise NotImplementedError


class ParseError(Exception):
    """Raised when a page cannot be parsed at all."""
