"""Barebones transliteration: everything -> plain ASCII.

Pipeline:
  1. Latin scripts: NFD-decompose and drop combining marks (e -> e), then apply
     an explicit map for non-decomposable glyphs (c -> c, ss -> ss, ...).
  2. Hanzi runs -> pinyin (syllable-spaced) via pypinyin.
  3. Kana runs -> romaji (Hepburn) via pykakasi.
  4. Anything still non-ASCII is dropped (documented limitation).
"""

from __future__ import annotations

import re
import unicodedata

import pykakasi
from pypinyin import lazy_pinyin

_LATIN_MAP = str.maketrans({
    "ç": "c", "Ç": "C",
    "ø": "o", "Ø": "O",
    "æ": "ae", "Æ": "AE",
    "ß": "ss",
    "ð": "d", "Ð": "D",
    "þ": "th", "Þ": "Th",
    "ł": "l", "Ł": "L",
    "đ": "d", "Đ": "D",
    "ħ": "h", "Ħ": "H",
    "ı": "i", "İ": "I",
    "œ": "oe", "Œ": "OE",
    "ŋ": "ng", "Ŋ": "Ng",
})

_HANZI_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]+")
_KANA_RE = re.compile(
    r"[\u3040-\u309f\u30a0-\u30ff\uff66-\uff9f]+"
)

_kakasi = pykakasi.kakasi()


def _latin_to_ascii(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.translate(_LATIN_MAP)
    return "".join(ch for ch in text if ord(ch) < 128)


def _kana_to_romaji(run: str) -> str:
    run = unicodedata.normalize("NFKC", run)
    return "".join(part["hepburn"] for part in _kakasi.convert(run))


def to_ascii(text: str) -> str:
    """Transliterate ``text`` to plain ASCII, best-effort."""
    segments: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        if buffer:
            segments.append(_latin_to_ascii("".join(buffer)).strip())
            buffer.clear()

    pos = 0
    while pos < len(text):
        hanzi = _HANZI_RE.match(text, pos)
        kana = _KANA_RE.match(text, pos)
        if hanzi:
            flush()
            segments.append(" ".join(lazy_pinyin(hanzi.group())))
            pos = hanzi.end()
        elif kana:
            flush()
            segments.append(_kana_to_romaji(kana.group()))
            pos = kana.end()
        else:
            buffer.append(text[pos])
            pos += 1
    flush()
    return " ".join(segment for segment in segments if segment)
