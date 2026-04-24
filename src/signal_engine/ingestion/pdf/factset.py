"""Block-level parsing for FactSet CallStreet transcripts.

Consumes the line-level output of `factset_patterns` and produces the
final `(utterances, corporate_roster, analyst_roster, stats)` tuple.
"""

from __future__ import annotations

from signal_engine.ingestion.pdf.factset_patterns import (
    DOT_SEPARATOR_RE,
    NAME_RE,
    OPERATOR_INLINE_RE,
    QA_MARKER_RE,
    ROLE_HINT_RE,
    detect_section,
    strip_boilerplate,
)


def parse_participants(lines: list[str], start: int) -> tuple[dict[str, str], int]:
    """Parse a (name, role) participant block. Stops at section or dotted line."""
    roster: dict[str, str] = {}
    i = start
    while i < len(lines):
        line = lines[i]
        if detect_section(line) is not None or DOT_SEPARATOR_RE.match(line):
            break
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        if NAME_RE.match(stripped) and (i + 1) < len(lines):
            role_line = lines[i + 1].strip()
            if ROLE_HINT_RE.search(role_line):
                roster[stripped] = role_line
                i += 2
                continue
        i += 1
    return roster, i


def split_into_blocks(lines: list[str]) -> list[list[str]]:
    """Split a run of lines on dotted-separator lines. Empty blocks dropped."""
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if DOT_SEPARATOR_RE.match(line):
            if current:
                blocks.append(current)
                current = []
            continue
        current.append(line)
    if current:
        blocks.append(current)
    return blocks


def parse_speaker_block(block: list[str]) -> list[tuple[str, str]]:
    """Parse one inter-dots block into (speaker, text) pairs.

    A block may contain multiple `Operator:` interjections; each becomes
    its own pair. Non-operator blocks typically yield one (speaker, text).
    """
    out: list[tuple[str, str]] = []
    while block and not block[0].strip():
        block.pop(0)
    while block and not block[-1].strip():
        block.pop()
    if not block:
        return out

    first = block[0].strip()
    op_m = OPERATOR_INLINE_RE.match(first)
    if op_m:
        remainder = [op_m.group(1)] + block[1:]
        text = " ".join(l.strip() for l in remainder if l.strip())
        if text:
            out.append(("Operator", text))
        return out

    name_candidate = first
    if not NAME_RE.match(name_candidate):
        text = " ".join(l.strip() for l in block if l.strip())
        if text:
            out.append(("Unknown", text))
        return out

    idx = 1
    if idx < len(block) and ROLE_HINT_RE.search(block[idx]):
        idx += 1
    if idx < len(block) and QA_MARKER_RE.match(block[idx]):
        idx += 1

    text_lines: list[str] = []
    for line in block[idx:]:
        mid_op = OPERATOR_INLINE_RE.match(line.strip())
        if mid_op:
            if text_lines:
                joined = " ".join(l.strip() for l in text_lines if l.strip()).strip()
                if joined:
                    out.append((name_candidate, joined))
                text_lines = []
            out.append(("Operator", mid_op.group(1).strip()))
            continue
        text_lines.append(line)

    if text_lines:
        joined = " ".join(l.strip() for l in text_lines if l.strip()).strip()
        if joined:
            out.append((name_candidate, joined))

    return out


def normalize_factset(raw_text: str) -> tuple[list[dict], dict[str, str], dict[str, str], dict]:
    """Returns (utterances, corporate_roster, analyst_roster, stats).

    Only content utterances (Prepared Remarks + Q&A) are returned.
    Bookkeeping segments (Header, Participants) are included in stats
    but not in the returned utterance list.
    """
    lines = strip_boilerplate(raw_text)
    corporate: dict[str, str] = {}
    analysts: dict[str, str] = {}
    utterances: list[dict] = []

    i = 0
    current_segment = "Header"
    body_buffer: list[str] = []

    def flush_body():
        nonlocal body_buffer
        if not body_buffer:
            return
        for block in split_into_blocks(body_buffer):
            for speaker, text in parse_speaker_block(block):
                utterances.append({
                    "speaker": speaker,
                    "segment": current_segment,
                    "text": text,
                })
        body_buffer = []

    while i < len(lines):
        sec = detect_section(lines[i])
        if sec is not None:
            flush_body()
            i += 1
            if sec == "Participants":
                new, i = parse_participants(lines, i)
                corporate.update(new)
                current_segment = "Participants"
                continue
            if sec == "Analyst Participants":
                new, i = parse_participants(lines, i)
                analysts.update(new)
                current_segment = "Analyst Participants"
                continue
            current_segment = sec
            continue
        body_buffer.append(lines[i])
        i += 1
    flush_body()

    content_segments = {"Prepared Remarks", "Q&A"}
    content = [u for u in utterances if u["segment"] in content_segments]
    stats = {
        "raw_line_count": len(lines),
        "utterance_count_total": len(utterances),
        "utterance_count_content": len(content),
        "segments_observed": sorted({u["segment"] for u in utterances}),
    }
    return content, corporate, analysts, stats
