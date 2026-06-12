"""Write events to iCalendar (.ics) text, importable into Google Calendar.

Deliberately dependency-free: the ICS we need (all-day VEVENTs) is simple
enough to write by hand, per RFC 5545.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterable
from datetime import timedelta

from dscal.models import Event


def _escape(text: str) -> str:
    """Escape text per RFC 5545 (backslash, semicolon, comma, newline)."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def _uid(event: Event) -> str:
    """Deterministic UID so re-imports update instead of duplicating."""
    raw = f"{event.course}|{event.label}|{event.date.isoformat()}"
    return hashlib.sha1(raw.encode()).hexdigest()[:16] + "@dscal"


def _fold(line: str) -> list[str]:
    """Fold lines longer than 75 octets per RFC 5545 section 3.1."""
    if len(line.encode()) <= 75:
        return [line]
    out: list[str] = []
    cur = ""
    for ch in line:
        if len((cur + ch).encode()) > (75 if not out else 74):
            out.append(cur if not out else " " + cur)
            cur = ch
        else:
            cur += ch
    if cur:
        out.append(cur if not out else " " + cur)
    return out


def to_ics(events: Iterable[Event]) -> str:
    """Render events as an ICS calendar of all-day events.

    Event titles are deliberately bare -- "DSC 80: LAB 1" -- per the
    calendar spec: simple, scannable, no links.
    """
    lines: list[str] = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//dscal//dscal//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:DSC course deadlines",
    ]
    for event in sorted(events):
        start = event.date.strftime("%Y%m%d")
        end = (event.date + timedelta(days=1)).strftime("%Y%m%d")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{_uid(event)}",
                f"DTSTART;VALUE=DATE:{start}",
                f"DTEND;VALUE=DATE:{end}",
                f"SUMMARY:{_escape(event.summary)}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    folded: list[str] = []
    for line in lines:
        folded.extend(_fold(line))
    return "\r\n".join(folded) + "\r\n"
