import pytest

from helpers import make_epub, make_pdf, make_pdf_no_outline
from nobs_txt.extractors import extract_book
from nobs_txt.model import Options, UnsupportedFormatError


def test_pdf_outline_chapters(tmp_path):
    book = extract_book(make_pdf(tmp_path), Options())
    assert book.title == "Fixture Book"
    assert book.chapter_source == "outline"
    assert [chapter.title for chapter in book.chapters] == ["Chapter 1"]
    text = " ".join(p for chapter in book.chapters for p in chapter.paragraphs)
    assert "page 1" in text
    assert "page 2" in text


def test_pdf_flat_no_outline(tmp_path):
    book = extract_book(make_pdf_no_outline(tmp_path), Options())
    assert book.chapter_source == "flat"
    assert len(book.chapters) == 1
    text = " ".join(book.chapters[0].paragraphs)
    assert "Chapter 1" in text
    assert "Chapter 3" in text


def test_pdf_flat_split_fallback(tmp_path):
    book = extract_book(make_pdf_no_outline(tmp_path), Options(split_chapters=True))
    assert [chapter.title for chapter in book.chapters] == [
        "Chapter 1",
        "Chapter 2",
        "Chapter 3",
    ]


def test_epub_spine(tmp_path):
    book = extract_book(make_epub(tmp_path), Options())
    assert book.title == "Fixture EPUB"
    assert book.chapter_source == "spine"
    assert [chapter.title for chapter in book.chapters] == ["Chapter 1", "Chapter 2"]
    assert any("Hello world" in paragraph for paragraph in book.chapters[0].paragraphs)


def test_epub_split(tmp_path):
    book = extract_book(make_epub(tmp_path), Options(split_chapters=True))
    assert len(book.chapters) == 2


def test_unsupported_format(tmp_path):
    target = tmp_path / "book.docx"
    target.write_text("x")
    with pytest.raises(UnsupportedFormatError):
        extract_book(target, Options())
