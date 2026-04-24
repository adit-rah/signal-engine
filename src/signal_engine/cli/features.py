"""CLI: extract features from Normalized Documents."""

from __future__ import annotations

import argparse
import sys

from signal_engine.analysis.features import (
    extract_transcript_features,
    iter_press_release_stems,
    iter_transcript_dates,
    write_features,
)
from signal_engine.analysis.press_release_features import extract_press_release_features
from signal_engine.config.companies import load_v1_companies
from signal_engine.config.lexicons import load_hedging_lexicon
from signal_engine.domain.entity import load_entity_by_ticker
from signal_engine.paths import relative


def _entity_as_dict(e) -> dict:
    """Convert Entity dataclass to the dict shape the library expects."""
    return {
        "canonical_id": e.canonical_id,
        "ticker": e.ticker,
        "speakers": e.speakers_as_dicts(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["transcript", "press_release", "all"],
                        help="Single-doc mode, or 'all' to sweep a ticker (or every v1 ticker).")
    parser.add_argument("ticker", nargs="?", default=None,
                        help="Ticker symbol. Omit with 'all' mode to sweep all v1 tickers.")
    parser.add_argument("date_or_stem", nargs="?", default=None,
                        help="Date (YYYY-MM-DD) for transcripts, or file stem for press_release.")
    args = parser.parse_args()

    entities_by_ticker = {k: _entity_as_dict(v) for k, v in load_entity_by_ticker().items()}
    hedges, boosters = load_hedging_lexicon()

    if args.mode == "all":
        if args.ticker:
            tickers = [args.ticker.upper()]
        else:
            tickers = [c["ticker"].upper() for c in load_v1_companies()]
        total = 0
        for t in tickers:
            if t not in entities_by_ticker:
                print(f"[{t}] unknown ticker (not in config/entities.json), skipping")
                continue
            entity = entities_by_ticker[t]
            n = 0
            for date in iter_transcript_dates(t):
                feats = extract_transcript_features(t, date, entity, hedges, boosters)
                out = write_features(feats)
                n += 1
                print(f"[{t}] transcript  {date}  -> {relative(out)}")
            for stem in iter_press_release_stems(t):
                feats = extract_press_release_features(t, stem, entity, hedges, boosters)
                out = write_features(feats)
                n += 1
                print(f"[{t}] press_rel   {stem[:25]}…  -> {relative(out)}")
            print(f"[{t}] {n} documents featurized")
            total += n
        print(f"\nTotal: {total} document feature bundles written")
        return

    if not args.ticker or not args.date_or_stem:
        print("Error: single-doc mode requires ticker and date_or_stem", file=sys.stderr)
        sys.exit(2)
    ticker = args.ticker.upper()
    if ticker not in entities_by_ticker:
        raise SystemExit(f"Unknown ticker {ticker}; update config/entities.json")
    entity = entities_by_ticker[ticker]

    if args.mode == "transcript":
        feats = extract_transcript_features(ticker, args.date_or_stem, entity, hedges, boosters)
    else:
        feats = extract_press_release_features(ticker, args.date_or_stem, entity, hedges, boosters)
    out = write_features(feats)
    print(f"Wrote: {relative(out)}")


if __name__ == "__main__":
    main()
