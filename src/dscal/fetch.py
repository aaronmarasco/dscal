"""Network layer: fetch course pages, with an on-disk cache.

The only module that touches the network. Local file paths are accepted
in place of URLs (useful offline and for graders trying the tool without
a live quarter).
"""

from __future__ import annotations

import time
from pathlib import Path

import requests

CACHE_TTL_SECONDS = 3600
USER_AGENT = "dscal/0.1 (course deadline aggregator; personal use)"


def cache_dir() -> Path:
    return Path.home() / ".cache" / "dscal"


def fetch(url_or_path: str, *, key: str, refresh: bool = False) -> str:
    """Return page HTML, from cache if fresh, else from the network.

    If the network fails but a stale cache exists, returns the stale copy
    (better a slightly old answer than none).
    """
    path = Path(url_or_path).expanduser()
    if path.exists():
        return path.read_text(encoding="utf-8")

    cached = cache_dir() / f"{key}.html"
    if not refresh and cached.exists():
        age = time.time() - cached.stat().st_mtime
        if age < CACHE_TTL_SECONDS:
            return cached.read_text(encoding="utf-8")

    try:
        resp = requests.get(
            url_or_path, headers={"User-Agent": USER_AGENT}, timeout=15
        )
        resp.raise_for_status()
    except requests.RequestException:
        if cached.exists():
            return cached.read_text(encoding="utf-8")
        raise
    cache_dir().mkdir(parents=True, exist_ok=True)
    cached.write_text(resp.text, encoding="utf-8")
    return resp.text
