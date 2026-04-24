"""Wayback Machine snapshot URL lookup."""

from __future__ import annotations

from urllib.parse import quote

import requests

from signal_engine.ingestion.audio.http import HEADERS


def wayback_snapshot_urls(url: str, limit: int = 10) -> list[str]:
    """Query the CDX API for snapshots of `url`. Most-recent-first."""
    cdx = (
        "https://web.archive.org/cdx/search/cdx"
        f"?url={quote(url, safe='')}"
        f"&output=json&limit={-limit}&fl=timestamp,original"
    )
    try:
        resp = requests.get(cdx, headers=HEADERS, timeout=30)
    except requests.RequestException as exc:
        print(f"  wayback: {type(exc).__name__}: {exc}")
        return []
    if resp.status_code != 200:
        print(f"  wayback: CDX API status={resp.status_code}")
        return []
    try:
        rows = resp.json()
    except ValueError:
        print(f"  wayback: CDX API returned non-JSON (len={len(resp.text)})")
        return []
    if not rows or len(rows) < 2:
        print(f"  wayback: no snapshots found for {url}")
        return []
    return [f"https://web.archive.org/web/{ts}/{orig}" for ts, orig in rows[1:]]
