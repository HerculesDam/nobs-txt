"""Text cleaning: ligatures, smart punctuation, special spaces.

Every cleaning step is safe to apply line-by-line and is enabled by default
(disable via ``Options.clean``).
"""

from __future__ import annotations

import re
import unicodedata

_LIGATURES = str.maketrans({
    "\ufb00": "ff", "\ufb01": "fi", "\ufb02": "fl",
    "\ufb03": "ffi", "\ufb04": "ffl", "\ufb05": "st", "\ufb06": "st",
})

_SMART_PUNCT = str.maketrans({
    "\u201c": '"', "\u201d": '"', "\u201e": '"', "\u201f": '"',
    "\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'",
    "\u2013": "-", "\u2014": "-", "\u2015": "-", "\u2012": "-",
    "\u2010": "-", "\u2011": "-",
    "\u2026": "...",
    "\u2022": "*",
})

#: Special spaces and zero-width characters that must never reach the output.
_SPECIAL_SPACES = {
    "\u00a0": " ",  # no-break space
    "\u2007": " ",  # figure space
    "\u2008": " ",  # punctuation space
    "\u2009": " ",  # thin space
    "\u200a": " ",  # hair space
    "\u202f": " ",  # narrow no-break space
    "\u205f": " ",  # medium mathematical space
    "\u3000": " ",  # ideographic space
    "\u200b": "",   # zero-width space
    "\u200c": "",   # zero-width non-joiner
    "\u200d": "",   # zero-width joiner
    "\ufeff": "",   # zero-width no-break space / BOM
    "\u00ad": "",   # soft hyphen
}

_SPACE_RE = re.compile(r"[ \t\f\v]+")

#: A line that is only a page number (1-4 digits).
_STRAY_DIGIT_LINE_RE = re.compile(r"^\s*\d{1,4}\s*$")
#: Page number glued to the previous word with a hyphen ("as-93") or a
#: punctuation mark ("frioquente, 11"). 3+ digit numbers keep the word when
#: separated by a plain space (years, counts); ranges like "1999-2000" are
#: safe because their second half has 4 digits.
_GLUED_HYPHEN_RE = re.compile(r"[-–—]\s*\d{1,3}\s*$")
_GLUED_PUNCT_RE = re.compile(r"[,;:]\s*\d{1,3}\s*$")


def strip_number_artifacts(paragraph: str) -> str:
    """Remove printed page-number artifacts embedded in the text.

    Handles standalone digit lines ("97") and numbers glued to a word at the
    end of a line ("as-93", "frioquente, 11"). Years and other 4+ digit
    numbers are left alone.
    """
    lines = paragraph.split("\n")
    kept: list[str] = []
    for line in lines:
        line = line.rstrip()
        if _STRAY_DIGIT_LINE_RE.match(line):
            continue
        line = _GLUED_HYPHEN_RE.sub("", line)
        line = _GLUED_PUNCT_RE.sub("", line)
        if line.strip():
            kept.append(line)
    return "\n".join(kept)


def clean_text(text: str) -> str:
    """Apply the full cleaning pipeline to a single line of text."""
    text = unicodedata.normalize("NFC", text)
    text = text.translate(_LIGATURES)
    text = text.translate(_SMART_PUNCT)
    text = "".join(_SPECIAL_SPACES.get(ch, ch) for ch in text)
    text = _SPACE_RE.sub(" ", text)
    return text.strip()


def assemble_paragraph(lines: list[str], fix_hyphens: bool = True) -> str:
    """Join extracted lines into one paragraph string.

    Embedded newlines mark preserved line breaks (reflow can join them later).
    When ``fix_hyphens`` is enabled, a line ending with ``-`` is merged with the
    next line when that line starts with a lowercase letter, undoing PDF
    hyphenation ("super-" + "market" -> "supermarket").
    """
    parts: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if (
            fix_hyphens
            and parts
            and parts[-1].endswith("-")
            and line[:1].islower()
        ):
            parts[-1] = parts[-1][:-1] + line
        else:
            parts.append(line)
    return "\n".join(parts)
