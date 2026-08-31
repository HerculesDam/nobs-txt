from nobs_txt.reflow import reflow_paragraph


def test_reflow_joins_lines():
    assert reflow_paragraph("line one\nline two") == "line one line two"


def test_reflow_collapses_spacing():
    assert reflow_paragraph("a  \nb") == "a b"


def test_reflow_single_line_unchanged():
    assert reflow_paragraph("only one") == "only one"
