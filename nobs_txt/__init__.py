"""nobs-txt — No bs TXT converter."""

from __future__ import annotations

from pathlib import Path

from .extractors import extract_book
from .model import Book, Chapter, Options, UnsupportedFormatError
from .writer import book_base_name, write_book

__version__ = "0.1.0"

__all__ = ["Book", "Chapter", "Options", "UnsupportedFormatError", "run"]


def run(input_path: str | Path, options: Options) -> list[Path]:
    """Convert ``input_path`` according to ``options``; return written files."""
    path = Path(input_path)
    book = extract_book(path, options)
    base = book_base_name(book, path)
    out_dir = options.out_dir or path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    return write_book(book, options, out_dir, base)
