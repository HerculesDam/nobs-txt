"""Input format dispatch."""

from __future__ import annotations

from pathlib import Path

from .. import split as split_mod
from ..model import Book, Options, UnsupportedFormatError


def extract_book(path: str | Path, options: Options) -> Book:
    """Extract a Book from ``path`` based on its file extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        from .pdf import extract_pdf

        book = extract_pdf(path, options)
    elif suffix == ".epub":
        from .epub import extract_epub

        book = extract_epub(path, options)
    else:
        raise UnsupportedFormatError(
            f"Unsupported file type {suffix or '(none)'!r}: "
            "only .pdf and .epub are supported."
        )

    # PDFs without an outline have no structure yet: fall back to heading regexes.
    if options.split_chapters and book.chapter_source == "flat":
        book.chapters = split_mod.split_by_headings(
            book.chapters, options.chapter_patterns
        )
    return book
