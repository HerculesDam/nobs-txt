from nobs_txt.model import Chapter
from nobs_txt.split import DEFAULT_PATTERNS, is_heading, split_by_headings


def test_is_heading_english():
    assert is_heading("Chapter 12", DEFAULT_PATTERNS)


def test_is_heading_spanish():
    assert is_heading("Capítulo 3", DEFAULT_PATTERNS)


def test_is_heading_chinese():
    assert is_heading("第3章", DEFAULT_PATTERNS)


def test_is_heading_numbered():
    assert is_heading("5. The Road Ahead", DEFAULT_PATTERNS)


def test_long_line_rejected():
    assert not is_heading("Chapter 1 " + "x" * 90, DEFAULT_PATTERNS)


def test_not_a_heading():
    assert not is_heading("The quick brown fox jumps", DEFAULT_PATTERNS)


def test_split_english():
    chapter = Chapter(None, ["Chapter 1", "Text one.", "Chapter 2", "Text two."])
    out = split_by_headings([chapter], DEFAULT_PATTERNS)
    assert [c.title for c in out] == ["Chapter 1", "Chapter 2"]
    assert out[0].paragraphs == ["Text one."]
    assert out[1].paragraphs == ["Text two."]


def test_split_keeps_existing_title():
    chapter = Chapter("Prologue", ["text", "Chapter 1", "more"])
    out = split_by_headings([chapter], DEFAULT_PATTERNS)
    assert out[0].title == "Prologue"
    assert out[1].title == "Chapter 1"


def test_no_headings_unchanged():
    chapter = Chapter(None, ["Just prose.", "More prose."])
    out = split_by_headings([chapter], DEFAULT_PATTERNS)
    assert out == [chapter]


def test_custom_patterns():
    chapter = Chapter(None, ["PROLOGUE", "text", "EPILOGUE", "more"])
    out = split_by_headings([chapter], [r"^PROLOGUE$", r"^EPILOGUE$"])
    assert [c.title for c in out] == ["PROLOGUE", "EPILOGUE"]
