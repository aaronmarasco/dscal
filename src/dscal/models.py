"""Core data model: a dated event on a course website."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class Kind(Enum):
    """What sort of schedule entry an event is."""

    LECTURE = "lecture"
    DISCUSSION = "discussion"
    LAB = "lab"
    PROJECT = "project"
    HOMEWORK = "homework"
    EXAM = "exam"
    OTHER = "other"

    @property
    def is_deadline(self) -> bool:
        """True if this kind of event represents work due (or an exam)."""
        return self in _DEADLINE_KINDS


_DEADLINE_KINDS = frozenset(
    {Kind.LAB, Kind.PROJECT, Kind.HOMEWORK, Kind.EXAM}
)


@dataclass(frozen=True, order=True)
class Event:
    """A single dated entry parsed from a course website."""

    date: date
    course: str  # e.g. "DSC 80"
    label: str  # e.g. "PROJ 1"
    title: str  # e.g. "Project 1 checkpoint"
    kind: Kind = Kind.OTHER
    url: str | None = None


def events_in_window(
    events: list[Event], start: date, days: int = 7
) -> list[Event]:
    """Events with start <= event.date < start + days, sorted by date."""
    end = start + timedelta(days=days)
    return sorted(e for e in events if start <= e.date < end)
