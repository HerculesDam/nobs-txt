"""Shared fixtures: tiny PDFs and EPUBs generated at test time."""

from __future__ import annotations

from pathlib import Path


def make_pdf(tmp_path: Path) -> Path:
    """Two-page PDF with a text layer, metadata title and a bookmark outline."""
    import fitz

    doc = fitz.open()
    doc.set_metadata({"title": "Fixture Book"})
    for index in range(2):
        page = doc.new_page()
        page.insert_text((72, 72), f"This is paragraph content on page {index + 1}.")
        page.insert_text((72, 300), f"More content on page {index + 1}.")
    doc.set_toc([[1, "Chapter 1", 1]])
    target = tmp_path / "book.pdf"
    doc.save(target)
    doc.close()
    return target


def make_pdf_no_outline(tmp_path: Path, pages: int = 3) -> Path:
    """Multi-page PDF without an outline; page starts read "Chapter N"."""
    import fitz

    doc = fitz.open()
    doc.set_metadata({"title": "No Outline Book"})
    for index in range(pages):
        page = doc.new_page()
        page.insert_text((72, 200), f"Chapter {index + 1}")
        page.insert_text((72, 240), f"Body text of chapter {index + 1}.")
    target = tmp_path / "no_outline.pdf"
    doc.save(target)
    doc.close()
    return target


def make_epub(tmp_path: Path) -> Path:
    """Two-chapter EPUB with a DC title and h1 headings."""
    from ebooklib import epub

    book = epub.EpubBook()
    book.set_identifier("fixture-001")
    book.set_title("Fixture EPUB")
    book.set_language("en")

    c1 = epub.EpubHtml(title="Chapter 1", file_name="chap_01.xhtml", uid="c1", lang="en")
    c1.content = (
        "<html><head><title>Chapter 1</title></head><body>"
        "<h1>Chapter 1</h1><p>Hello world, this is content.</p>"
        "<p>A second paragraph.</p></body></html>"
    )
    c2 = epub.EpubHtml(title="Chapter 2", file_name="chap_02.xhtml", uid="c2", lang="en")
    c2.content = "<html><body><h1>Chapter 2</h1><p>Goodbye world.</p></body></html>"
    book.add_item(c1)
    book.add_item(c2)
    book.toc = (
        epub.Link("chap_01.xhtml", "Chapter 1", "c1"),
        epub.Link("chap_02.xhtml", "Chapter 2", "c2"),
    )
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ["nav", c1, c2]

    target = tmp_path / "book.epub"
    epub.write_epub(str(target), book)
    return target
