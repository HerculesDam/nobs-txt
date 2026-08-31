"""Core data model shared across the pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Chapter:
    """A single logical chapter of a book."""

    title: str | None = None
    #: Paragraphs of cleaned text. Embedded newlines preserve original line
    #: breaks when reflow is disabled.
    paragraphs: list[str] = field(default_factory=list)


@dataclass
class Book:
    """A fully extracted book, ready for cleaning and writing."""

    title: str | None = None
    chapters: list[Chapter] = field(default_factory=list)
    #: How chapters were detected: "outline" (PDF bookmarks), "spine" (EPUB
    #: structure), or "flat" (no structure found yet).
    chapter_source: str = "flat"


@dataclass
class Options:
    """User-controllable conversion options."""

    mode: str = "full"            # "full" | "barebones"
    encoding: str = "utf-8"       # "utf-8" | "ascii"
    reflow: bool = False          # join wrapped lines into paragraphs
    no_breaks: bool = False       # output as one continuous line (no newlines)
    split_chapters: bool = False  # write one file per chapter
    strip_framing: bool = True    # remove headers/footers/page numbers
    strip_numbers: bool = False   # remove stray/glued page-number artifacts
    clean: bool = True            # punctuation/ligature/space cleaning
    hyphenation: bool = True      # fix hyphenation across line breaks
    chapter_patterns: list[str] | None = None  # override heading regexes
    out_dir: Path | None = None   # output directory (None = input's folder)


class UnsupportedFormatError(Exception):
    """Raised when the input file type is not supported."""
