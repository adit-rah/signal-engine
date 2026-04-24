"""Regex patterns + line-level filters for the FactSet CallStreet format.

Separated from `factset.py` so the patterns are easy to review and
extend without scrolling through block-level parsing logic. NVIDIA,
INTC, META and other Q4 Inc. hosted IR sites use this format.
"""

from __future__ import annotations

import re


DOT_SEPARATOR_RE = re.compile(r"^\s*\.{20,}\s*$")

SECTION_MARKERS = [
    (re.compile(r"^\s*(corporate participants|company participants)\s*$", re.IGNORECASE),
     "Participants"),
    (re.compile(r"^\s*(other participants|analyst participants|conference call participants)\s*$",
                re.IGNORECASE),
     "Analyst Participants"),
    (re.compile(r"^\s*(management discussion section|presentation|prepared remarks)\s*$",
                re.IGNORECASE),
     "Prepared Remarks"),
    (re.compile(
        r"^\s*(question\s+and\s+answer\s+section|question[-\s]?and[-\s]?answer(\s+session)?|"
        r"q\s*&\s*a|questions and answers)\s*$",
        re.IGNORECASE),
     "Q&A"),
]

BOILERPLATE_SUBSTRINGS = [
    "1-877-FACTSET",
    "www.callstreet.com",
    "Copyright ©",
    "Total Pages:",
    "Corrected Transcript",
]
BARE_LINE_PATTERNS = [
    re.compile(r"^\s*\d+\s*$"),
    re.compile(r"^\s*NVIDIA Corp\.?\s*\(NVDA\)\s*$", re.IGNORECASE),
    re.compile(r"^\s*Q[1-4]\s+\d{4}\s+Earnings\s+Call\s*$", re.IGNORECASE),
    re.compile(r"^\s*\d{1,2}-[A-Z][a-z]{2}-\d{4}\s*$"),
    re.compile(r"^\s*$"),
]

NAME_RE = re.compile(
    r"^[A-Z][A-Za-z.'-]+(?:\s+[A-Z]\.)?(?:\s+[A-Z][A-Za-z.'-]+){0,4}$"
)
ROLE_HINT_RE = re.compile(
    r"\b(officer|president|chair|director|founder|chief|vice president|"
    r"analyst|managing|partner|investor relations|head of|executive)\b",
    re.IGNORECASE,
)
QA_MARKER_RE = re.compile(r"^\s*[QA]\s*$")
OPERATOR_INLINE_RE = re.compile(r"^\s*Operator\s*[:\-]\s*(.*)$")


def is_boilerplate(line: str) -> bool:
    if any(sub in line for sub in BOILERPLATE_SUBSTRINGS):
        return True
    return any(pat.match(line) for pat in BARE_LINE_PATTERNS)


def strip_boilerplate(raw_text: str) -> list[str]:
    return [l for l in raw_text.splitlines() if not is_boilerplate(l)]


def detect_section(line: str) -> str | None:
    stripped = line.strip()
    for pat, label in SECTION_MARKERS:
        if pat.match(stripped):
            return label
    return None
