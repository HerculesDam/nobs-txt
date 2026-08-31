"""PDF extraction via PyMuPDF (text layer only)."""

from __future__ import annotations

import statistics
import unicodedata
from pathlib import Path

from ..clean import assemble_paragraph, clean_text
from ..framing import Page, PageLine, strip_framing
from ..model import Book, Chapter, Options

TOP_LEVEL = 1


def _page_lines(page) -> list[PageLine]:
    raw = page.get_text("dict")
    lines: list[PageLine] = []
    for block in raw.get("blocks", []):
        if block.get("type") != 0:  # skip images
            continue
        for line in block.get("lines", []):
            text = "".join(span.get("text", "") for span in line.get("spans", []))
            text = text.strip()
            if not text:
                continue
            _, y0, _, y1 = line["bbox"]
            lines.append(PageLine(text=text, y0=y0, y1=y1))
    return lines


def _assemble(lines: list[PageLine], options: Options) -> str:
    if options.clean:
        texts = [clean_text(line.text) for line in lines]
    else:
        texts = [line.text.strip() for line in lines]
    return assemble_paragraph(texts, fix_hyphens=options.hyphenation)


def _group_paragraphs(page: Page, options: Options) -> list[str]:
    """Group a page's lines into paragraphs using vertical-gap heuristics."""
    lines = sorted(page.lines, key=lambda line: (round(line.y0, 1), line.text))
    heights = [line.y1 - line.y0 for line in lines if line.y1 > line.y0]
    median = statistics.median(heights) if heights else 12.0
    gap_threshold = median * 1.5

    paragraphs: list[str] = []
    current: list[PageLine] = []
    for line in lines:
        if current and line.y0 - current[-1].y1 > gap_threshold:
            paragraphs.append(_assemble(current, options))
            current = []
        current.append(line)
    if current:
        paragraphs.append(_assemble(current, options))
    return paragraphs


def _normalize(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).strip().lower().split())


def _strip_matching_heading(chapter: Chapter) -> None:
    """Drop the body line that duplicates the chapter's outline title.

    The heading often shares a paragraph with body text (small vertical gap in
    the PDF), so only the first line is removed in that case.
    """
    if not chapter.title or not chapter.paragraphs:
        return
    title = _normalize(chapter.title)
    if not title:
        return
    for index, paragraph in enumerate(chapter.paragraphs[:3]):
        first_line, sep, rest = paragraph.partition("\n")
        if len(first_line) <= 80 and _normalize(first_line) == title:
            if sep:
                chapter.paragraphs[index] = rest.lstrip()
            else:
                del chapter.paragraphs[index]
            return


def extract_pdf(path: str | Path, options: Options) -> Book:
    import fitz

    doc = fitz.open(path)
    try:
        metadata = doc.metadata or {}
        title = (metadata.get("title") or "").strip() or None

        pages: list[Page] = []
        for number in range(doc.page_count):
            page = doc.load_page(number)
            pages.append(Page(lines=_page_lines(page), height=page.rect.height))

        if options.strip_framing:
            pages = strip_framing(pages)

        page_paragraphs = [_group_paragraphs(page, options) for page in pages]

        toc = doc.get_toc(simple=True) or []
        top_level = [entry for entry in toc if entry[0] == TOP_LEVEL]

        if top_level:
            chapters: list[Chapter] = []
            for index, (_level, toc_title, toc_page) in enumerate(top_level):
                start = toc_page - 1  # get_toc pages are 1-based
                end = (
                    top_level[index + 1][2] - 1
                    if index + 1 < len(top_level)
                    else doc.page_count
                )
                paragraphs = [
                    paragraph
                    for page in page_paragraphs[start:end]
                    for paragraph in page
                ]
                chapter = Chapter(title=toc_title.strip() or None, paragraphs=paragraphs)
                _strip_matching_heading(chapter)
                chapters.append(chapter)
            return Book(title=title, chapters=chapters, chapter_source="outline")

        all_paragraphs = [paragraph for page in page_paragraphs for paragraph in page]
        return Book(
            title=title,
            chapters=[Chapter(title=title, paragraphs=all_paragraphs)],
            chapter_source="flat",
        )
    finally:
        doc.close()
