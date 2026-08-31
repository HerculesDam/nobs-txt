# nobs-txt

**No bs TXT converter** — turns PDF/EPUB books (text layer only) into the
simplest possible plain-text output: no fancy characters, no formatting; at
most a blank line between paragraphs.

## Features

- **Two character modes**
  - `full` (default): keeps real characters (`ç`, `é`, CJK…), only normalizes
    punctuation/whitespace.
  - `barebones`: transliterates everything to plain ASCII — `é → e`, `ç → c`,
    hanzi → pinyin (`中文 → "zhong wen"`), kana → romaji (`ひらがな → "hiragana"`).
- **Cleaning pipeline** (all on by default, each disable-able): smart quotes
  and dashes → ASCII, ligatures (`ﬁ → fi`), special/zero-width spaces removed,
  hyphenation across line breaks fixed, headers/footers/page numbers stripped.
- **Optional paragraph reflow** (`--reflow`): join wrapped lines into real
  paragraphs.
- **Optional chapter splitting** (`--split-chapters`): PDF bookmarks → EPUB
  structure → heading regex fallback (EN/ES/中文, overridable), writing one
  `.txt` per chapter plus the combined file.
- **UTF-8 or ASCII output**, LF line endings.
- **Two interfaces**: a flag-based CLI and an interactive wizard (run with no
  arguments).

## Install

```bash
python -m pip install -e .
```

## Usage

```bash
# flags (defaults shown)
nobs-txt book.pdf --mode full --encoding utf-8
nobs-txt book.epub --mode barebones --encoding ascii --reflow --split-chapters

# interactive wizard
nobs-txt
```

| Flag | Meaning |
| --- | --- |
| `--mode {full,barebones}` | character handling (default `full`) |
| `--encoding {utf-8,ascii}` | output encoding; `ascii` transliterates (default `utf-8`) |
| `--reflow` | join wrapped lines into paragraphs |
| `--split-chapters` | write per-chapter files + combined file |
| `--chapter-patterns RE[,RE...]` | override default heading regexes |
| `--no-framing` | keep headers, footers and page numbers |
| `--no-clean` | skip punctuation/ligature/space cleaning |
| `--no-hyphenation` | keep PDF-style hyphenation at line breaks |
| `--out DIR` | output directory (default: the input's folder) |
| `--wizard` | force the interactive wizard |

Output files are named after the book title (PDF metadata / EPUB `dc:title`),
falling back to the input filename: `The Book.txt`, `The Book-chapter-01.txt`…

## Limitations

- Text-layer documents only — no OCR for scanned pages.
- Barebones mode drops characters it cannot transliterate (e.g., Greek,
  Korean Hangul) — documented trade-off, not a bug.
- Hyphenation fixes merge `super-` + `market` into `supermarket`; compound
  words broken across lines ("well-" + "known") are merged without the hyphen.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```
