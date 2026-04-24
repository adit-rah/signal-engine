"""Shared SGML parsing for SEC EDGAR 8-K filings.

Every 8-K full-submission.txt begins with an SEC-HEADER block and
contains one or more TYPE-tagged exhibits. This module parses the header
and extracts exhibit bodies. Both `press_releases.py` (extraction) and
`pdf.manifest` (earnings-date harvesting) depend on it.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser


def parse_sec_header(text: str) -> dict:
    header_match = re.search(r"<SEC-HEADER>(.*?)</SEC-HEADER>", text, re.DOTALL)
    if not header_match:
        return {}
    header = header_match.group(1)

    def _field(pattern: str, default: str = "") -> str:
        m = re.search(pattern, header)
        return m.group(1).strip() if m else default

    items = [
        m.group(1).strip()
        for m in re.finditer(r"ITEM INFORMATION:\s*(.+)", header)
    ]
    filed_raw = _field(r"FILED AS OF DATE:\s*(\d{8})")
    period_raw = _field(r"CONFORMED PERIOD OF REPORT:\s*(\d{8})")

    return {
        "accession_number": _field(r"ACCESSION NUMBER:\s*(\S+)"),
        "form_type": _field(r"CONFORMED SUBMISSION TYPE:\s*(\S+)"),
        "filed_date": _fmt_date(filed_raw),
        "period_of_report": _fmt_date(period_raw),
        "items": items,
        "cik": _field(r"CENTRAL INDEX KEY:\s*(\d+)"),
        "company_name": _field(r"COMPANY CONFORMED NAME:\s*(.+?)\n"),
    }


def _fmt_date(yyyymmdd: str) -> str:
    if not yyyymmdd or len(yyyymmdd) != 8:
        return ""
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def is_earnings_filing(items: list[str]) -> bool:
    """Item 2.02 is 'Results of Operations and Financial Condition'."""
    return any("results of operations" in item.lower() for item in items)


def extract_exhibit(text: str, exhibit_type: str) -> str | None:
    """Extract the body of a TYPE-tagged exhibit (e.g. 'EX-99.1').

    Non-greedy match tolerates intervening FILENAME/DESCRIPTION tags.
    """
    pattern = rf"<TYPE>{re.escape(exhibit_type)}\b.*?<TEXT>(.*?)</TEXT>"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1) if m else None


class HTMLStripper(HTMLParser):
    """Convert HTML to plain text, collapsing whitespace and preserving paragraphs."""

    SKIP_TAGS = {"script", "style", "head"}

    def __init__(self) -> None:
        super().__init__()
        self._out: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth += 1
        elif tag in {"p", "div", "br", "tr", "h1", "h2", "h3", "h4", "li"}:
            self._out.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.SKIP_TAGS:
            self._skip_depth = max(0, self._skip_depth - 1)
        elif tag in {"p", "div", "tr", "h1", "h2", "h3", "h4", "li"}:
            self._out.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self._out.append(data)

    def text(self) -> str:
        raw = "".join(self._out)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n[ \t]+", "\n", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()
