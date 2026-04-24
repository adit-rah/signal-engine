"""Regex patterns for earnings-call discovery and Q&A segmentation."""

from __future__ import annotations

import re


EARNINGS_LINK_PATTERNS = [
    r"earnings",
    r"quarterly",
    r"\bq[1-4]\b",
    r"first quarter",
    r"second quarter",
    r"third quarter",
    r"fourth quarter",
    r"fy ?\d",
    r"fiscal",
    r"webcast",
    r"replay",
    r"conference call",
]
EARNINGS_LINK_RE = re.compile("|".join(EARNINGS_LINK_PATTERNS), re.IGNORECASE)

MEDIA_HOST_PATTERNS = [
    r"edge\.media-server\.com",
    r"event\.on24\.com",
    r"players?\.brightcove\.(net|com)",
    r"bcove\.video",
    r"vidyard\.com",
    r"wistia\.(net|com)",
    r"vimeo\.com",
    r"youtube\.com",
    r"youtu\.be",
    r"services\.choruscall\.com",
    r"\.m3u8(\?|$)",
    r"\.mp3(\?|$)",
    r"\.m4a(\?|$)",
]
MEDIA_URL_RE = re.compile("|".join(MEDIA_HOST_PATTERNS), re.IGNORECASE)


QA_START_PATTERNS = [
    r"question[- ]and[- ]answer",
    r"\bq\s*&\s*a\b",
    r"we will now (?:take|begin taking) (?:your )?questions",
    r"operator.*will now (?:open|conduct|begin) the (?:lines? )?(?:question|for questions)",
    r"first question (?:comes from|today comes from)",
    r"open (?:the line|the call|up) (?:for|to) (?:questions|q ?& ?a)",
]
QA_START_RE = re.compile("|".join(QA_START_PATTERNS), re.IGNORECASE)


MONTHS = {
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
