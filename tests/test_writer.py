from nobs_txt.model import Book, Chapter, Options
from nobs_txt.writer import book_base_name, sanitize_title, write_book


def _book() -> Book:
    return Book(
        title="The Great Book",
        chapters=[
            Chapter(title="Chapter 1", paragraphs=["line one\nline two", "second para"]),
            Chapter(title=None, paragraphs=["closing"]),
        ],
    )


def test_sanitize_title():
    assert sanitize_title('Weird: "Title"? / Bad*') == "Weird Title Bad"


def test_base_name_uses_metadata(tmp_path):
    assert book_base_name(_book(), tmp_path / "whatever.pdf") == "The Great Book"


def test_base_name_falls_back_to_filename(tmp_path):
    book = Book(title=None, chapters=[Chapter()])
    assert book_base_name(book, tmp_path / "my novel.pdf") == "my novel"


def test_combined_file(tmp_path):
    files = write_book(_book(), Options(), tmp_path, "The Great Book")
    assert [file.name for file in files] == ["The Great Book.txt"]
    text = (tmp_path / "The Great Book.txt").read_text(encoding="utf-8")
    assert "Chapter 1" in text
    assert "second para" in text
    assert "closing" in text


def test_split_chapter_files(tmp_path):
    files = write_book(_book(), Options(split_chapters=True), tmp_path, "The Great Book")
    names = sorted(file.name for file in files)
    assert names == [
        "The Great Book-chapter-01.txt",
        "The Great Book-chapter-02.txt",
        "The Great Book.txt",
    ]
    first = (tmp_path / "The Great Book-chapter-01.txt").read_text(encoding="utf-8")
    assert first == "Chapter 1\n\nline one\nline two\n\nsecond para"


def test_reflow(tmp_path):
    write_book(_book(), Options(reflow=True), tmp_path, "Book")
    text = (tmp_path / "Book.txt").read_text(encoding="utf-8")
    assert "line one line two" in text
    assert "line one\nline two" not in text


def test_ascii_transliterates(tmp_path):
    book = Book(title="Café", chapters=[Chapter(title=None, paragraphs=["café naïve"])])
    write_book(book, Options(mode="full", encoding="ascii"), tmp_path, "Caf")
    data = (tmp_path / "Caf.txt").read_bytes()
    assert all(byte < 128 for byte in data)
    assert data == b"cafe naive"


def test_barebones_utf8(tmp_path):
    book = Book(title="Café", chapters=[Chapter(title=None, paragraphs=["café ção"])])
    write_book(book, Options(mode="barebones", encoding="utf-8"), tmp_path, "Caf")
    assert (tmp_path / "Caf.txt").read_text(encoding="utf-8") == "cafe cao"


def test_full_mode_keeps_unicode(tmp_path):
    book = Book(title="Café", chapters=[Chapter(title=None, paragraphs=["café ção"])])
    write_book(book, Options(mode="full", encoding="utf-8"), tmp_path, "Caf")
    assert (tmp_path / "Caf.txt").read_text(encoding="utf-8") == "café ção"


def test_no_breaks_single_line(tmp_path):
    book = Book(
        title="T",
        chapters=[
            Chapter(title="Chapter 1", paragraphs=["line one\nline two", "second para"]),
            Chapter(title=None, paragraphs=["closing"]),
        ],
    )
    write_book(book, Options(no_breaks=True), tmp_path, "Flat")
    text = (tmp_path / "Flat.txt").read_text(encoding="utf-8")
    assert "\n" not in text
    assert text == "Chapter 1 line one line two second para closing"


def test_no_breaks_respects_strip_numbers(tmp_path):
    book = Book(
        title="T",
        chapters=[Chapter(title=None, paragraphs=["as-93\nand later", "97", "a word, 11\nend"])],
    )
    write_book(book, Options(no_breaks=True, strip_numbers=True), tmp_path, "Flat")
    text = (tmp_path / "Flat.txt").read_text(encoding="utf-8")
    assert "\n" not in text
    assert "as-93" not in text
    assert " 97 " not in text
    assert "word, 11" not in text


def test_strip_numbers_keeps_years_and_ranges(tmp_path):
    book = Book(
        title="T",
        chapters=[Chapter(title=None, paragraphs=["em 1999 e 1999-2000", "42"])],
    )
    write_book(book, Options(strip_numbers=True), tmp_path, "Flat")
    text = (tmp_path / "Flat.txt").read_text(encoding="utf-8")
    assert "1999" in text
    assert "2000" in text
    assert "42" not in text
