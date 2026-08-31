"""Heading-regex chapter detection (fallback when the source has no structure)."""

from __future__ import annotations

import re

from .model import Chapter

MAX_HEADING_LEN = 80

DEFAULT_PATTERNS = [
    r"^Chapter\s+\d+",
    r"^CHAPTER\s+\d+",
    r"^Cap[íi]tulo\s+\d+",
    r"^CAP[ÍI]TULO\s+\d+",
    r"^第[0-9一二三四五六七八九十百千万零两]{1,6}[章节卷]",
    r"^\d{1,3}\.\s+\S",
]

_PATTERN_CACHE: dict[tuple[str, ...], list[re.Pattern]] = {}


def _compile(patterns: list[str] | None) -> list[re.Pattern]:
    key = tuple(patterns or DEFAULT_PATTERNS)
    if key not in _PATTERN_CACHE:
        _PATTERN_CACHE[key] = [re.compile(pattern) for pattern in key]
    return _PATTERN_CACHE[key]


def is_heading(paragraph: str, patterns: list[str] | None) -> bool:
    """True if the first line of ``paragraph`` looks like a chapter heading."""
    first_line = paragraph.split("\n", 1)[0].strip()
    if not first_line or len(first_line) > MAX_HEADING_LEN:
        return False
    return any(pattern.match(first_line) for pattern in _compile(patterns))


def split_by_headings(
    chapters: list[Chapter], patterns: list[str] | None
) -> list[Chapter]:
    """Split chapters at heading lines.

    Returns the input list unchanged when no headings are found anywhere.
    """
    result: list[Chapter] = []
    found = False
    for chapter in chapters:
        current: list[str] = []
        current_title = chapter.title
        for paragraph in chapter.paragraphs:
            if is_heading(paragraph, patterns):
                found = True
                if current:
                    result.append(Chapter(title=current_title, paragraphs=current))
                    current = []
                current_title = paragraph.split("\n", 1)[0].strip()
            else:
                current.append(paragraph)
        result.append(Chapter(title=current_title, paragraphs=current))
    return result if found else chapters
