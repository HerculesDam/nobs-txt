from nobs_txt.clean import assemble_paragraph, clean_text, strip_number_artifacts


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


def test_strip_standalone_digit_line():
    assert strip_number_artifacts("97") == ""
    assert strip_number_artifacts(" 9 \n") == ""


def test_strip_glued_hyphen_number():
    assert strip_number_artifacts("sobre as-93") == "sobre as"


def test_strip_glued_punct_number():
    assert strip_number_artifacts("frioquente, 11") == "frioquente"
    assert strip_number_artifacts("frioquente; 11") == "frioquente"


def test_strip_multiline_paragraph():
    text = "primeira linha\n97\nsegunda as-93"
    assert strip_number_artifacts(text) == "primeira linha\nsegunda as"


def test_keeps_years_and_ranges():
    assert strip_number_artifacts("em 1999") == "em 1999"
    assert strip_number_artifacts("1999-2000") == "1999-2000"


def test_keeps_normal_numbers():
    assert strip_number_artifacts("o numero 42 e a pagina 100") == "o numero 42 e a pagina 100"
