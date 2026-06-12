"""Core data model: a dated event on a course website."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, timedelta
from enum import Enum


class Kind(Enum):
    """What sort of schedule entry an event is (used for display)."""

    LECTURE = "lecture"
    DISCUSSION = "discussion"
    LAB = "lab"
    PROJECT = "project"
    HOMEWORK = "homework"
    QUIZ = "quiz"
    EXAM = "exam"
    OTHER = "other"


@dataclass(frozen=True, order=True)
class Event:
    """A single dated entry parsed from a course website."""

    date: date
    course: str  # e.g. "DSC 80"
    label: str  # normalized, e.g. "LAB 1", "FINAL PROJ", "EXAM"
    kind: Kind = Kind.OTHER

    @property
    def summary(self) -> str:
        """Calendar title: course + bare label, nothing else."""
        return f"{self.course}: {self.label}"


# The deliverables worth putting on a calendar. Anything else on a course
# schedule (LEC, DISC, REV, BONUS, SUR, PRAC, "QUIZ 1 SOLUTIONS", ...)
# fails this pattern.
_DEADLINE_RE = re.compile(r"^(FINAL PROJ|LAB|HW|QUIZ|PROJ|EXAM)( \d+)?$")


def normalize_label(raw: str) -> str:
    """Uppercase, collapse whitespace, split glued digits: "HW1" -> "HW 1"."""
    label = " ".join(raw.upper().split())
    return re.sub(r"(?<=[A-Z])(?=\d)", " ", label)


def is_deadline(label: str) -> bool:
    """True if a normalized label is a deliverable (lab/hw/quiz/proj/exam)."""
    return _DEADLINE_RE.match(label) is not None


def events_in_window(events: list[Event], start: date, days: int = 7) -> list[Event]:
    """Events with start <= event.date < start + days, sorted by date."""
    end = start + timedelta(days=days)
    return sorted(e for e in events if start <= e.date < end)
