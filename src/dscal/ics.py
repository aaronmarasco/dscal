"""Write events to iCalendar (.ics) text, importable into Google Calendar.

Deliberately dependency-free: the ICS we need (all-day VEVENTs) is simple
enough to write by hand, per RFC 5545.
"""

from __future__ import annotations

from collections.abc import Iterable

from dscal.models import Event


def to_ics(events: Iterable[Event]) -> str:
    """Render events as an ICS calendar of all-day events.

    Each event gets a deterministic UID so re-imports update rather than
    duplicate. Text fields are escaped per RFC 5545.
    """
    raise NotImplementedError
