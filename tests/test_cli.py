import pytest

from helpers import make_epub, make_pdf, make_pdf_no_outline
from nobs_txt import cli


def test_cli_barebones_ascii(tmp_path):
    pdf = make_pdf(tmp_path)
    rc = cli.main([str(pdf), "--mode", "barebones", "--encoding", "ascii", "--reflow"])
    assert rc == 0
    out = tmp_path / "Fixture Book.txt"
    assert out.exists()
    assert all(byte < 128 for byte in out.read_bytes())


def test_cli_split_chapters(tmp_path):
    pdf = make_pdf_no_outline(tmp_path)
    rc = cli.main([str(pdf), "--split-chapters"])
    assert rc == 0
    assert (tmp_path / "No Outline Book-chapter-01.txt").exists()
    assert (tmp_path / "No Outline Book-chapter-03.txt").exists()


def test_cli_epub(tmp_path):
    epub = make_epub(tmp_path)
    rc = cli.main([str(epub), "--split-chapters"])
    assert rc == 0
    assert (tmp_path / "Fixture EPUB.txt").exists()
    assert (tmp_path / "Fixture EPUB-chapter-01.txt").exists()
    assert (tmp_path / "Fixture EPUB-chapter-02.txt").exists()


def test_cli_out_dir(tmp_path):
    pdf = make_pdf(tmp_path)
    out = tmp_path / "converted"
    rc = cli.main([str(pdf), "--out", str(out)])
    assert rc == 0
    assert (out / "Fixture Book.txt").exists()


def test_cli_unsupported_format(tmp_path, capsys):
    target = tmp_path / "book.docx"
    target.write_text("x")
    rc = cli.main([str(target)])
    assert rc == 1
    assert "Unsupported file type" in capsys.readouterr().err


def test_cli_wizard_flow(monkeypatch, tmp_path):
    pdf = make_pdf(tmp_path)
    answers = iter([str(pdf), "", "", "", "", "", "", "", "", "", "", ""])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    rc = cli.main([])
    assert rc == 0
    assert (tmp_path / "Fixture Book.txt").exists()


def test_cli_version(capsys):
    with pytest.raises(SystemExit) as exc:
        cli.main(["--version"])
    assert exc.value.code == 0
    assert "nobs-txt" in capsys.readouterr().out
