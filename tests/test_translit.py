from nobs_txt.translit import to_ascii


def test_latin_diacritics_stripped():
    assert to_ascii("café façada ñoño") == "cafe facada nono"


def test_latin_special_glyphs_mapped():
    assert to_ascii("ç ø æ ß ð þ ł đ") == "c o ae ss d th l d"


def test_hanzi_to_pinyin():
    assert to_ascii("中文") == "zhong wen"


def test_kana_to_romaji():
    assert to_ascii("ひらがな") == "hiragana"


def test_mixed_scripts_spaced():
    assert to_ascii("漢字ひらがな") == "han zi hiragana"
    assert to_ascii("Hello 世界") == "Hello shi jie"


def test_ascii_passthrough():
    assert to_ascii("Hello, world! 123") == "Hello, world! 123"


def test_unrepresentable_dropped():
    assert to_ascii("αβγ") == ""
