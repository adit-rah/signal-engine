"""CLI: extract earnings press releases from SEC 8-K filings."""

from __future__ import annotations

import argparse

from signal_engine.ingestion.edgar.press_releases import extract_all_press_releases
from signal_engine.paths import PRESS_RELEASE_INDEX, relative


def main() -> None:
    argparse.ArgumentParser(description=__doc__).parse_args()
    records = extract_all_press_releases()

    print()
    print(f"Total filings processed: {len(records)}")
    print(f"Earnings filings: {sum(1 for r in records if r.is_earnings)}")
    print(f"Press releases extracted: "
          f"{sum(1 for r in records if r.normalized_text_path)}")
    print(f"Index: {relative(PRESS_RELEASE_INDEX)}")


if __name__ == "__main__":
    main()
