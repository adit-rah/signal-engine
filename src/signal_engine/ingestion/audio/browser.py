"""Playwright-based page fetcher for Cloudflare-protected IR sites.

Lazily starts a single Chromium context and reuses it for the lifetime
of the process. Callers typically want a process-wide singleton, which
is why `_BROWSER_CONTEXT` is module-level state.
"""

from __future__ import annotations

from signal_engine.ingestion.audio.http import HEADERS


_BROWSER_CONTEXT = None


def get_browser_context():
    """Lazily start Playwright and return a ready-to-use browser context."""
    global _BROWSER_CONTEXT
    if _BROWSER_CONTEXT is not None:
        return _BROWSER_CONTEXT
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "--browser requested but Playwright is not installed.\n"
            "Run: uv add playwright && uv run playwright install chromium"
        )
    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=HEADERS["User-Agent"],
        viewport={"width": 1280, "height": 900},
    )
    _BROWSER_CONTEXT = context
    print("  playwright: Chromium context started")
    return context


def fetch_html_browser(url: str, timeout: int = 30, verbose: bool = False) -> str | None:
    """Fetch via Playwright Chromium. Waits for Cloudflare-style challenges to clear."""
    context = get_browser_context()
    page = context.new_page()
    try:
        resp = page.goto(url, timeout=timeout * 1000, wait_until="networkidle")
        page.wait_for_timeout(3000)
        status = resp.status if resp else 0
        content = page.content()
        if verbose or status != 200:
            print(f"  playwright: status={status} url={page.url}")
        if "Just a moment" in content[:1000] or "challenge-platform" in content[:2000]:
            page.wait_for_timeout(5000)
            content = page.content()
        if status == 200 or ("Just a moment" not in content[:1000]):
            return content
        return None
    except Exception as exc:
        print(f"  playwright: {type(exc).__name__}: {exc}")
        return None
    finally:
        page.close()
