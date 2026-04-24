"""Regex patterns and parsers for transcript-PDF discovery.

Separated from `discover.py` so the patterns are easy to review and
extend without scrolling through Playwright setup. The patterns here
match conventions observed across Q4 Inc.-hosted IR sites:

    NVDA-Q3-2026-Earnings-Call-19-November-2025-5_00-PM-ET.pdf
    META-Q4-2025-Earnings-Call-Transcript.pdf
    /doc_financials/2025/q4/META-Q4-2025-...
    Q4-2018-earnings-call-transcript.pdf
"""

from __future__ import annotations

import re


TRANSCRIPT_FILENAME_RE = re.compile(
    r"earnings[-_ ]?call"
    r"|earnings[-_ ]?conference"
    r"|conference[-_ ]?call"
    r"|earnings[-_ ]?transcript"
    r"|call[-_ ]?transcript"
    r"|quarterly[-_ ]?earnings",
    re.IGNORECASE,
)

DATE_IN_FILENAME_RE = re.compile(
    r"(\d{1,2})[-_ ](jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|"
    r"jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|"
    r"nov(?:ember)?|dec(?:ember)?)[-_ ](20\d{2})",
    re.IGNORECASE,
)

Q_YEAR_IN_PATH_RE = re.compile(
    r"Q([1-4])[- _'](\d{4}|\d{2})"
    r"|/(\d{4})/q([1-4])/",
    re.IGNORECASE,
)

MONTH_MAP = {
    "jan": "01", "january": "01",
    "feb": "02", "february": "02",
    "mar": "03", "march": "03",
    "apr": "04", "april": "04",
    "may": "05",
    "jun": "06", "june": "06",
    "jul": "07", "july": "07",
    "aug": "08", "august": "08",
    "sep": "09", "sept": "09", "september": "09",
    "oct": "10", "october": "10",
    "nov": "11", "november": "11",
    "dec": "12", "december": "12",
}


def parse_date_from_filename(filename: str) -> str:
    m = DATE_IN_FILENAME_RE.search(filename)
    if not m:
        return ""
    day, month, year = m.groups()
    mo = MONTH_MAP[month.lower()]
    return f"{year}-{mo}-{int(day):02d}"


def parse_q_year_from_url(url: str) -> tuple[int, int]:
    """Extract (fiscal_quarter, year) from a URL/filename when possible.

    Returns (0, 0) if nothing parses. Year is the 4-digit value present
    in the URL; downstream reconciles it against SEC dates.
    """
    m = Q_YEAR_IN_PATH_RE.search(url)
    if not m:
        return 0, 0
    if m.group(1):
        q = int(m.group(1))
        y = m.group(2)
        year = int(y) if len(y) == 4 else 2000 + int(y)
    else:
        year = int(m.group(3))
        q = int(m.group(4))
    return q, year
