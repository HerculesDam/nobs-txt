"""Output writing: combined + per-chapter .txt files, encodings, title naming."""

from __future__ import annotations

import re
from pathlib import Path

from .model import Book, Chapter, Options
from .reflow import reflow_paragraph
from .translit import to_ascii

_ILLEGAL_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def sanitize_title(title: str) -> str:
    """Turn a book title into something safe for a Windows/Unix filename."""
    title = _ILLEGAL_RE.sub("", title).strip()
    title = re.sub(r"\s+", " ", title)
    return title[:120].rstrip(" .")


def book_base_name(book: Book, input_path: str | Path) -> str:
    """Base name for output files: book title, else the input filename stem."""
    title = (book.title or "").strip() or Path(input_path).stem
    base = sanitize_title(title)
    return base or "book"


def _transliterate(text: str, options: Options) -> str:
    if options.mode == "barebones" or options.encoding == "ascii":
        return to_ascii(text)
    return text


def chapter_text(chapter: Chapter, options: Options) -> str:
    """Render one chapter as plain text (title line + blank-separated paragraphs)."""
    parts: list[str] = []
    if chapter.title:
        parts.append(chapter.title)
    for paragraph in chapter.paragraphs:
        parts.append(reflow_paragraph(paragraph) if options.reflow else paragraph)
    return "\n\n".join(_transliterate(part, options) for part in parts if part)


def write_book(book: Book, options: Options, out_dir: Path, base: str) -> list[Path]:
    """Write the combined file (and per-chapter files when requested)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    combined = out_dir / f"{base}.txt"
    body = "\n\n".join(chapter_text(chapter, options) for chapter in book.chapters)
    combined.write_text(body + ("\n" if body else ""), encoding=options.encoding, newline="\n")
    written.append(combined)

    if options.split_chapters:
        width = max(2, len(str(len(book.chapters))))
        for index, chapter in enumerate(book.chapters, start=1):
            target = out_dir / f"{base}-chapter-{index:0{width}d}.txt"
            body = chapter_text(chapter, options)
            target.write_text(
                body + ("\n" if body else ""), encoding=options.encoding, newline="\n"
            )
            written.append(target)
    return written
