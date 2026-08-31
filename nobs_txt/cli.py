"""Command-line interface for nobs-txt."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, run
from .model import Options, UnsupportedFormatError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nobs-txt",
        description="No bs TXT converter: PDF/EPUB -> plain text.",
        epilog="Run without arguments to launch the interactive wizard.",
    )
    parser.add_argument("input", nargs="?", help="path to a .pdf or .epub file")
    parser.add_argument(
        "--mode",
        choices=("full", "barebones"),
        default="full",
        help="character handling (default: full)",
    )
    parser.add_argument(
        "--encoding",
        choices=("utf-8", "ascii"),
        default="utf-8",
        help="output encoding (default: utf-8; ascii transliterates)",
    )
    parser.add_argument(
        "--reflow",
        action="store_true",
        help="join wrapped lines into paragraphs",
    )
    parser.add_argument(
        "--no-breaks",
        action="store_true",
        help="output the whole book as one continuous line (no newlines)",
    )
    parser.add_argument(
        "--strip-numbers",
        action="store_true",
        help="remove stray page numbers and numbers glued to words (as-93)",
    )
    parser.add_argument(
        "--split-chapters",
        action="store_true",
        help="write one file per chapter plus the combined file",
    )
    parser.add_argument(
        "--chapter-patterns",
        metavar="RE[,RE...]",
        help="override the default chapter-heading regexes",
    )
    parser.add_argument(
        "--no-framing",
        action="store_false",
        dest="strip_framing",
        help="keep headers, footers and page numbers",
    )
    parser.add_argument(
        "--no-clean",
        action="store_false",
        dest="clean",
        help="skip punctuation/ligature/space cleaning",
    )
    parser.add_argument(
        "--no-hyphenation",
        action="store_false",
        dest="hyphenation",
        help="keep PDF-style hyphenation at line breaks",
    )
    parser.add_argument(
        "--out",
        metavar="DIR",
        default=None,
        help="output directory (default: the input's folder)",
    )
    parser.add_argument(
        "--wizard",
        action="store_true",
        help="launch the interactive wizard",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.set_defaults(strip_framing=True, clean=True, hyphenation=True)
    return parser


def _options_from_args(args: argparse.Namespace) -> Options:
    return Options(
        mode=args.mode,
        encoding=args.encoding,
        reflow=args.reflow,
        no_breaks=args.no_breaks,
        split_chapters=args.split_chapters,
        strip_framing=args.strip_framing,
        strip_numbers=args.strip_numbers,
        clean=args.clean,
        hyphenation=args.hyphenation,
        chapter_patterns=(
            [pattern.strip() for pattern in args.chapter_patterns.split(",") if pattern.strip()]
            if args.chapter_patterns
            else None
        ),
        out_dir=Path(args.out) if args.out else None,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.wizard or args.input is None:
        from .wizard import run_wizard

        return run_wizard()

    options = _options_from_args(args)
    try:
        files = run(args.input, options)
    except (UnsupportedFormatError, ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for target in files:
        print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
