"""Safe header/footer and page-number stripping.

Heuristic, applied per page before paragraph grouping:
  * standalone page numbers in the top/bottom 12% band are dropped;
  * "Page X of Y" lines in the band are dropped;
  * short lines (<= 40 chars) repeated at the same band on >= max(3, 40%) of
    the pages are treated as running headers/footers and dropped everywhere.

Middle-of-page lines are never touched.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

BAND_RATIO = 0.12
MAX_RUNNING_LEN = 40
_PAGE_NO_RE = re.compile(
    r"^\s*(?:\d{1,5}|[ivxlcdm]{1,6})\s*$", re.IGNORECASE
)
_PAGE_X_OF_Y_RE = re.compile(
    r"^\s*page\s*\d+\s*(?:of|/)\s*\d+\s*$",
    re.IGNORECASE,
)
_SPACE_RE = re.compile(r"\s+", re.UNICODE)


@dataclass
class PageLine:
    """A single text line extracted from a page, with its vertical extent."""

    text: str
    y0: float
    y1: float


@dataclass
class Page:
    """All text lines of one page plus its height (for band math)."""

    lines: list[PageLine]
    height: float


def _band(y0: float, y1: float, height: float) -> str | None:
    if y0 < BAND_RATIO * height:
        return "top"
    if y1 > (1 - BAND_RATIO) * height:
        return "bottom"
    return None


def _normalize(text: str) -> str:
    return _SPACE_RE.sub(" ", unicodedata.normalize("NFC", text).strip().lower())


def strip_framing(pages: list[Page]) -> list[Page]:
    """Return new Page objects with framing lines removed."""
    if not pages:
        return pages
    total = len(pages)
    min_repeats = max(3, math.ceil(total * 0.4))

    # Count short top/bottom lines that repeat across pages.
    counts: dict[tuple[str, str], int] = {}
    for page in pages:
        for line in page.lines:
            band = _band(line.y0, line.y1, page.height)
            text = line.text.strip()
            if band is None or not text or len(text) > MAX_RUNNING_LEN:
                continue
            key = (_normalize(text), band)
            counts[key] = counts.get(key, 0) + 1

    running = {key for key, count in counts.items() if count >= min_repeats}

    stripped: list[Page] = []
    for page in pages:
        kept: list[PageLine] = []
        for line in page.lines:
            band = _band(line.y0, line.y1, page.height)
            text = line.text.strip()
            if band is not None and text:
                if _PAGE_NO_RE.match(text) or _PAGE_X_OF_Y_RE.match(text):
                    continue
                if (_normalize(text), band) in running:
                    continue
            kept.append(line)
        stripped.append(Page(lines=kept, height=page.height))
    return stripped
