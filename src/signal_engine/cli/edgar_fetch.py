"""CLI: pull 8-K filings from SEC EDGAR for one or more tickers."""

from __future__ import annotations

import argparse

from signal_engine.ingestion.edgar.fetch import fetch_filings
from signal_engine.paths import RAW_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tickers", nargs="+", help="One or more ticker symbols")
    parser.add_argument("--after", default="2019-01-01",
                        help="Earliest filing date (YYYY-MM-DD). Default: 2019-01-01")
    parser.add_argument("--form", default="8-K",
                        help="SEC form type (default: 8-K). Also useful: 10-K, 10-Q.")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading into: {RAW_DIR}")
    print(f"Tickers: {', '.join(args.tickers)}")
    print(f"Form: {args.form}")
    print(f"After: {args.after}")
    print()

    for ticker, count in fetch_filings(args.tickers, after=args.after, form=args.form).items():
        print(f"[{ticker}] downloaded {count} filings")
    print()
    print("Done.")


if __name__ == "__main__":
    main()
