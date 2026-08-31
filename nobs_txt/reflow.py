"""Paragraph reflow: turn preserved line breaks into plain spaces."""

from __future__ import annotations

import re

_SPACE_RE = re.compile(r"[ 	\f\v]+")


def reflow_paragraph(paragraph: str) -> str:
    """Join the lines of a paragraph into a single line.

    Called only when ``Options.reflow`` is enabled. Paragraphs never contain
    blank lines (they are split on those), so every embedded newline is a
    wrapped line.
    """
    return _SPACE_RE.sub(" ", paragraph.replace("\n", " ")).strip()
