"""Course list stored at ~/.config/dscal/courses.toml.

Format:

    [courses.dsc80]
    name = "DSC 80"
    url = "https://dsc80.com"
"""

from __future__ import annotations

import os

try:  # tomllib is stdlib from 3.11; tomli is the identical backport
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Course:
    key: str  # e.g. "dsc80"
    name: str  # e.g. "DSC 80"
    url: str  # site URL, or a local path for offline/demo use


def config_path() -> Path:
    base = os.environ.get("DSCAL_CONFIG_DIR")
    if base:
        return Path(base) / "courses.toml"
    return Path.home() / ".config" / "dscal" / "courses.toml"


def load_courses() -> list[Course]:
    path = config_path()
    if not path.exists():
        return []
    with path.open("rb") as f:
        data = tomllib.load(f)
    courses = []
    for key, entry in data.get("courses", {}).items():
        courses.append(
            Course(
                key=key,
                name=str(entry.get("name", key.upper())),
                url=str(entry["url"]),
            )
        )
    return courses


def save_courses(courses: list[Course]) -> None:
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for c in sorted(courses, key=lambda c: c.key):
        lines.append(f"[courses.{c.key}]")
        lines.append(f'name = "{c.name}"')
        lines.append(f'url = "{c.url}"')
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def slugify(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())
