"""EPUB extraction via ebooklib (text layer only)."""

from __future__ import annotations

import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Tag

from .. import split as split_mod
from ..clean import clean_text
from ..model import Book, Chapter, Options

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_BLOCK_LEAF_TAGS = {"p", "li", "blockquote", "pre"}
_CONTAINER_TAGS = {"div", "section", "article", "main", "body", "html"}
_ALL_BLOCK_TAGS = _HEADING_TAGS | _BLOCK_LEAF_TAGS | _CONTAINER_TAGS

_PUNCT_SPACE_RE = re.compile(r"\s+([,.;:!?])")


def _join_pending(pending: list[str]) -> str:
    text = "".join(pending)
    text = _PUNCT_SPACE_RE.sub(r"\1", text)
    return " ".join(text.split()).strip()


def _node_text(element) -> str:
    text = element.get_text(" ")
    text = _PUNCT_SPACE_RE.sub(r"\1", text)
    lines = [" ".join(line.split()) for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


def _walk(node, out: list[str], title: list[str | None], seen: list[bool]) -> None:
    """Walk the tree, emitting block text in document order."""
    pending: list[str] = []

    def flush() -> None:
        text = _join_pending(pending)
        pending.clear()
        if text:
            out.append(text)

    for child in node.children:
        if isinstance(child, NavigableString):
            pending.append(str(child))
            continue
        if not isinstance(child, Tag):
            continue
        name = child.name
        if name in _HEADING_TAGS:
            flush()
            text = _node_text(child)
            if not seen[0] and text:
                seen[0] = True
                title[0] = text
            elif text:
                out.append(text)
        elif name in _BLOCK_LEAF_TAGS:
            flush()
            text = _node_text(child)
            if text:
                out.append(text)
        elif name in _CONTAINER_TAGS:
            flush()
            _walk(child, out, title, seen)
        elif child.find(_ALL_BLOCK_TAGS):
            # Inline wrapper that unexpectedly contains blocks: recurse.
            flush()
            _walk(child, out, title, seen)
        else:
            pending.append(_node_text(child))
    flush()


def _html_to_paragraphs(content: bytes) -> tuple[str | None, list[str]]:
    soup = BeautifulSoup(content, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")

    title: list[str | None] = [None]
    seen_heading: list[bool] = [False]
    paragraphs: list[str] = []
    _walk(soup.body if soup.body is not None else soup, paragraphs, title, seen_heading)

    if not paragraphs and not title[0]:
        body = soup.get_text("\n")
        paragraphs = [line.strip() for line in body.split("\n") if line.strip()]
    return title[0], paragraphs


def _split_spine(chapters: list[Chapter], patterns: list[str] | None) -> list[Chapter]:
    result: list[Chapter] = []
    for chapter in chapters:
        parts = split_mod.split_by_headings([chapter], patterns)
        if len(parts) == 1 and parts[0] is chapter:
            result.append(chapter)
        else:
            result.extend(parts)
    return result


def extract_epub(path: str | Path, options: Options) -> Book:
    from ebooklib import ITEM_NAVIGATION, epub
    from ebooklib.epub import EpubNav

    book = epub.read_epub(str(path))

    dc_title = book.get_metadata("DC", "title")
    title = dc_title[0][0].strip() if dc_title else None

    by_id = {item.get_id(): item for item in book.get_items()}
    chapters: list[Chapter] = []
    for entry in book.spine:
        idref = entry[0] if isinstance(entry, (tuple, list)) else entry
        if not isinstance(idref, str) or idref not in by_id:
            continue
        item = by_id[idref]
        if item.get_type() == ITEM_NAVIGATION or isinstance(item, EpubNav):
            continue
        content = item.get_content()
        if not content:
            continue

        item_title, paragraphs = _html_to_paragraphs(content)
        if item_title is None:
            item_title = getattr(item, "title", None) or Path(item.get_name()).stem
        if options.clean:
            item_title = clean_text(item_title) if item_title else None
            paragraphs = [clean_text(paragraph) for paragraph in paragraphs]
        if paragraphs:
            chapters.append(Chapter(title=item_title, paragraphs=paragraphs))

    if not chapters:
        raise ValueError("EPUB contains no readable content.")

    if options.split_chapters:
        chapters = _split_spine(chapters, options.chapter_patterns)

    return Book(title=title, chapters=chapters, chapter_source="spine")
