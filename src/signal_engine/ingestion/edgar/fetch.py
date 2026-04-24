"""Library: fetch 8-K filings from SEC EDGAR.

Thin wrapper over `sec-edgar-downloader`. Raw SGML filings land under
data/raw/sec-edgar-filings/<TICKER>/<FORM>/. Extraction of the earnings
press release is a separate stage (`press_releases.py`).
"""

from __future__ import annotations

from sec_edgar_downloader import Downloader

from signal_engine.paths import RAW_DIR


EMAIL = "aditrahman5945@gmail.com"
COMPANY = "SignalEngine"


def fetch_filings(tickers: list[str], after: str, form: str = "8-K") -> dict[str, int]:
    """Download `form` filings for each ticker after the given date.

    Returns a ticker -> count map. The Downloader writes directly to
    data/raw/, so provenance is preserved as-delivered by SEC.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    dl = Downloader(COMPANY, EMAIL, str(RAW_DIR))
    counts: dict[str, int] = {}
    for ticker in tickers:
        counts[ticker] = dl.get(form, ticker, after=after)
    return counts
