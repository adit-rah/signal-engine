"""Plain-HTTP page fetcher for IR sites.

Used for IR pages that don't require a real browser. For Cloudflare-
protected sites, use `browser.py` instead.
"""

from __future__ import annotations

import requests

from signal_engine.io import USER_AGENT


HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def fetch_html(url: str, timeout: int = 20, verbose: bool = False) -> str | None:
    """Fetch a URL via requests. Returns None on non-200 or network failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        print(f"  fetch_html: {type(exc).__name__}: {exc}")
        return None

    if verbose or resp.status_code != 200:
        chain = (
            " -> ".join([r.url for r in resp.history] + [resp.url])
            if resp.history else resp.url
        )
        print(f"  fetch_html: status={resp.status_code} url={chain}")
        ctype = resp.headers.get("Content-Type", "")
        if ctype:
            print(f"  fetch_html: content-type={ctype}")
        if resp.status_code >= 400:
            snippet = resp.text[:300].replace("\n", " ").strip()
            if snippet:
                print(f"  fetch_html: body[:300]={snippet!r}")
                if "Just a moment" in resp.text[:1000]:
                    print("  fetch_html: looks like Cloudflare challenge — try --browser")

    if resp.status_code != 200:
        return None
    return resp.text
