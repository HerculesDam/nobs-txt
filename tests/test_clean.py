from nobs_txt.clean import assemble_paragraph, clean_text


def test_ligatures():
    assert clean_text("ﬁne ﬂow ﬀoo") == "fine flow ffoo"


def test_smart_quotes():
    assert clean_text("“hi”") == '"hi"'
    assert clean_text("‘yo’") == "'yo'"
    assert clean_text("‚low‘") == "'low'"


def test_dashes_and_ellipsis():
    assert clean_text("a — b – c …") == "a - b - c ..."


def test_bullet():
    assert clean_text("• item") == "* item"


def test_special_spaces():
    assert clean_text("a\u00a0b\u2009c\u202fd") == "a b c d"


def test_zero_width_and_soft_hyphen_removed():
    assert clean_text("ab\u200bcd\ufeffe") == "abcde"
    assert clean_text("soft\u00adhyphen") == "softhyphen"


def test_collapse_and_strip():
    assert clean_text("  a 	 b   ") == "a b"


def test_hyphen_join_on():
    assert assemble_paragraph(["super-", "market"], fix_hyphens=True) == "supermarket"


def test_hyphen_join_off():
    assert assemble_paragraph(["super-", "market"], fix_hyphens=False) == "super-\nmarket"


def test_hyphen_no_join_uppercase():
    assert assemble_paragraph(["See-", "John"], fix_hyphens=True) == "See-\nJohn"


def test_assemble_skips_empty_lines():
    assert assemble_paragraph(["one", "", "two"]) == "one\ntwo"
