"""Library: download a transcript PDF and extract its raw text.

The PDF itself is the Raw artifact (DATA_MODEL.md Raw layer); the
extracted text is also Raw (as-delivered pymupdf output).
"""

from __future__ import annotations

from pathlib import Path


def extract_text(pdf_path: Path) -> tuple[str, dict]:
    """Extract text from a PDF with pymupdf. Returns (text, metadata).

    Records per-page character offsets so downstream Span resolution
    can cite specific pages.
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        raise SystemExit("pymupdf is required. Run: uv add pymupdf")

    doc = fitz.open(str(pdf_path))
    pages_text: list[str] = []
    page_offsets: list[int] = []
    cursor = 0
    for page in doc:
        text = page.get_text("text")
        page_offsets.append(cursor)
        pages_text.append(text)
        cursor += len(text) + 2  # +2 for the "\n\n" joiner
    full = "\n\n".join(pages_text)
    meta = {
        "page_count": doc.page_count,
        "pdf_metadata": {k: v for k, v in doc.metadata.items() if v},
        "char_count": len(full),
        "page_char_offsets": page_offsets,
        "extracted_with": (
            f"pymupdf/{fitz.__doc__.splitlines()[0] if fitz.__doc__ else 'unknown'}"
        ),
    }
    doc.close()
    return full, meta
