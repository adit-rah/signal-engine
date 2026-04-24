"""CLI: discover earnings-call webcast URLs from an IR page."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict

from signal_engine.ingestion.audio.discover import discover
from signal_engine.paths import MANIFEST_DIR, relative


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("ticker", help="Uppercase ticker symbol")
    p.add_argument("start_url", help="Starting URL (IR quarterly-results page)")
    p.add_argument("--wayback", action="store_true",
                   help="Also try Wayback Machine snapshots for event pages without live media")
    p.add_argument("--verbose", action="store_true", help="Verbose link logging")
    p.add_argument("--browser", action="store_true",
                   help="Use Playwright (real Chromium) for fetches. "
                        "Needed when the site has Cloudflare / bot-detection. "
                        "Requires: `uv add playwright && uv run playwright install chromium`.")
    args = p.parse_args()

    ticker = args.ticker.upper()
    calls = discover(
        ticker, args.start_url, args.wayback, args.verbose, use_browser=args.browser
    )

    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    manifest_path = MANIFEST_DIR / f"{ticker}_earnings_calls.jsonl"
    with manifest_path.open("w", encoding="utf-8") as f:
        for call in calls:
            f.write(json.dumps(asdict(call)) + "\n")

    print()
    print(f"Discovered {len(calls)} call(s) with candidate media URLs.")
    print(f"Manifest: {relative(manifest_path)}")
    if not calls:
        print()
        print("NOTE: Zero calls found. Possible causes:")
        print("  - IR page uses JavaScript rendering (this script uses plain HTTP)")
        print("  - Start URL is wrong (try the Events & Presentations page)")
        print("  - Site blocks non-browser user agents")
        print("  - The content is purged and --wayback was not used")
        sys.exit(1)


if __name__ == "__main__":
    main()
