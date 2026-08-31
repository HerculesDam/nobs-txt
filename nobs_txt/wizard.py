"""Interactive wizard: guided prompts when no CLI flags are given."""

from __future__ import annotations

import sys
from pathlib import Path

from . import __version__, run
from .model import Options


def _prompt(message: str, default: str | None = None, required: bool = False) -> str:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        value = input(f"{message}{suffix}: ").strip().strip('"').strip("'")
        if not value and default is not None:
            return default
        if not value and required:
            print("This field is required.", file=sys.stderr)
            continue
        return value


def _yesno(message: str, default: bool) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        value = input(f"{message} [{hint}]: ").strip().lower()
        if not value:
            return default
        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False
        print("Please answer y or n.", file=sys.stderr)


def _choice(message: str, options: list[str], default: str) -> str:
    print(message)
    for index, option in enumerate(options, start=1):
        marker = " (default)" if option == default else ""
        print(f"  {index}. {option}{marker}")
    while True:
        value = input(f"Choose 1-{len(options)} [default: {default}]: ").strip()
        if not value:
            return default
        if value.isdigit() and 1 <= int(value) <= len(options):
            return options[int(value) - 1]
        if value in options:
            return value
        print("Invalid choice.", file=sys.stderr)


def _read_path() -> Path:
    while True:
        raw = input("PDF/EPUB file path: ").strip().strip('"').strip("'")
        path = Path(raw)
        if not path.is_file():
            print(f"No such file: {raw}", file=sys.stderr)
            continue
        if path.suffix.lower() not in (".pdf", ".epub"):
            print("Only .pdf and .epub files are supported.", file=sys.stderr)
            continue
        return path


def run_wizard() -> int:
    try:
        return _run_wizard()
    except EOFError:
        print("Input ended unexpectedly.", file=sys.stderr)
        return 1


def _run_wizard() -> int:
    print(f"nobs-txt v{__version__} - No bs TXT converter")
    print("Converts a PDF/EPUB book into the simplest possible plain text.")
    print()

    path = _read_path()
    mode = _choice("Character mode", ["full", "barebones"], default="full")
    encoding = _choice("Output encoding", ["utf-8", "ascii"], default="utf-8")
    reflow = _yesno("Join wrapped lines into paragraphs (reflow)", default=False)
    no_breaks = _yesno("Output as one continuous line (no line breaks)", default=False)
    strip_numbers = _yesno("Remove stray/glued page numbers", default=False)
    split = _yesno("Split chapters into separate files", default=False)
    framing = _yesno("Strip headers, footers and page numbers", default=True)
    clean = _yesno("Clean punctuation, ligatures and special spaces", default=True)
    hyphenation = _yesno("Fix hyphenation across line breaks", default=True)
    out_raw = _prompt("Output directory", default=str(path.parent))

    options = Options(
        mode=mode,
        encoding=encoding,
        reflow=reflow,
        no_breaks=no_breaks,
        split_chapters=split,
        strip_framing=framing,
        strip_numbers=strip_numbers,
        clean=clean,
        hyphenation=hyphenation,
        out_dir=Path(out_raw),
    )

    print()
    print("Ready to convert:")
    print(f"  input     : {path}")
    print(f"  mode      : {mode}")
    print(f"  encoding  : {encoding}")
    print(f"  reflow    : {'yes' if reflow else 'no'}")
    print(f"  no breaks : {'yes' if no_breaks else 'no'}")
    print(f"  split     : {'yes' if split else 'no'}")
    print(f"  output    : {out_raw}")
    if not _yesno("Proceed", default=True):
        print("Aborted.")
        return 1

    try:
        files = run(path, options)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for target in files:
        print(f"wrote {target}")
    return 0
