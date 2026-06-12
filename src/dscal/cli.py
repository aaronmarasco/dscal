"""Command-line interface for dscal."""

from __future__ import annotations

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table

from dscal import config, fetch
from dscal.models import Event, Kind, events_in_window
from dscal.parser import ParseError, parse_events

console = Console()

KIND_STYLES = {
    Kind.EXAM: "bold red",
    Kind.PROJECT: "bold magenta",
    Kind.LAB: "bold yellow",
    Kind.HOMEWORK: "bold yellow",
    Kind.DISCUSSION: "cyan",
    Kind.LECTURE: "dim",
    Kind.OTHER: "white",
}


def _collect(refresh: bool) -> list[Event]:
    courses = config.load_courses()
    if not courses:
        console.print(
            "[yellow]No courses configured.[/] Add one with: "
            "[bold]dscal add 'DSC 80' https://dsc80.com[/]"
        )
        sys.exit(1)
    events: list[Event] = []
    for course in courses:
        try:
            html = fetch.fetch(course.url, key=course.key, refresh=refresh)
        except Exception as exc:
            console.print(f"[red]{course.name}: fetch failed[/] ({exc})")
            continue
        try:
            found = parse_events(html, course=course.name)
        except ParseError as exc:
            console.print(f"[red]parse failed:[/] {exc}")
            continue
        if not found:
            console.print(
                f"[yellow]{course.name}: no schedule entries found[/] "
                "(unsupported site layout?)"
            )
            continue
        events.extend(found)
    return events


def cmd_add(args: argparse.Namespace) -> None:
    courses = config.load_courses()
    key = config.slugify(args.name)
    courses = [c for c in courses if c.key != key]
    courses.append(config.Course(key=key, name=args.name, url=args.url))
    config.save_courses(courses)
    console.print(f"Added [bold]{args.name}[/] -> {args.url}")


def cmd_remove(args: argparse.Namespace) -> None:
    courses = config.load_courses()
    key = config.slugify(args.name)
    kept = [c for c in courses if c.key != key]
    if len(kept) == len(courses):
        console.print(f"[yellow]No course named {args.name!r} found.[/]")
        sys.exit(1)
    config.save_courses(kept)
    console.print(f"Removed [bold]{args.name}[/]")


def cmd_list(args: argparse.Namespace) -> None:
    courses = config.load_courses()
    if not courses:
        console.print("No courses configured.")
        return
    for c in courses:
        console.print(f"[bold]{c.name}[/]  {c.url}")


def cmd_week(args: argparse.Namespace) -> None:
    events = _collect(args.refresh)
    if not args.all:
        events = [e for e in events if e.kind.is_deadline]
    today = date.today()
    window = events_in_window(events, start=today, days=args.days)
    if not window:
        console.print(
            f"[green]Nothing due in the next {args.days} days. :tada:[/]"
        )
        return
    table = Table(
        title=f"Due in the next {args.days} days",
        show_lines=False,
        header_style="bold",
    )
    table.add_column("When")
    table.add_column("Course")
    table.add_column("What")
    table.add_column("Title")
    table.add_column("Link", overflow="fold")
    for e in window:
        delta = (e.date - today).days
        when = {0: "TODAY", 1: "tomorrow"}.get(
            delta, e.date.strftime("%a %b %d")
        )
        style = "bold red" if delta <= 1 else KIND_STYLES.get(e.kind, "")
        table.add_row(
            f"[{style}]{when}[/]" if style else when,
            e.course,
            f"[{KIND_STYLES.get(e.kind, '')}]{e.label}[/]",
            e.title,
            e.url or "",
        )
    console.print(table)


def cmd_export(args: argparse.Namespace) -> None:
    from dscal.ics import to_ics

    events = _collect(args.refresh)
    if not args.all:
        events = [e for e in events if e.kind.is_deadline]
    if not events:
        console.print("[yellow]No events to export.[/]")
        sys.exit(1)
    out = Path(args.out)
    out.write_text(to_ics(events), encoding="utf-8", newline="")
    console.print(
        f"Wrote [bold]{len(events)}[/] events to [bold]{out}[/]. "
        "Import it at calendar.google.com -> Settings -> Import & export."
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="dscal",
        description=(
            "Deadlines from DSC course websites: weekly checkups in your "
            "terminal, and .ics export for Google Calendar."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_add = sub.add_parser("add", help="register a course website")
    p_add.add_argument("name", help='course name, e.g. "DSC 80"')
    p_add.add_argument("url", help="course site URL (or local HTML path)")
    p_add.set_defaults(func=cmd_add)

    p_rm = sub.add_parser("remove", help="remove a course")
    p_rm.add_argument("name")
    p_rm.set_defaults(func=cmd_remove)

    p_ls = sub.add_parser("list", help="show configured courses")
    p_ls.set_defaults(func=cmd_list)

    p_week = sub.add_parser(
        "week", help="what's due soon, across all courses"
    )
    p_week.add_argument("--days", type=int, default=7)
    p_week.add_argument(
        "--all", action="store_true", help="include lectures/discussions"
    )
    p_week.add_argument(
        "--refresh", action="store_true", help="ignore the cache"
    )
    p_week.set_defaults(func=cmd_week)

    p_exp = sub.add_parser(
        "export", help="write all deadlines to a Google Calendar .ics file"
    )
    p_exp.add_argument("--out", default="dsc-deadlines.ics")
    p_exp.add_argument(
        "--all", action="store_true", help="include lectures/discussions"
    )
    p_exp.add_argument(
        "--refresh", action="store_true", help="ignore the cache"
    )
    p_exp.set_defaults(func=cmd_export)

    args = parser.parse_args()
    args.func(args)
