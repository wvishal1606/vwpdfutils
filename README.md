# vwpdfutils

Command-line PDF utilities: compress, concat, booklet, split, rotate, and convert2pdf.

## Installation

```bash
pip install .
# development
pip install -e ".[dev]"
```

Runtime dependency: **`pypdf[full]`** (includes PyCryptodome for encrypted PDFs and Pillow for images).

## Global options

```text
vwpdfutils [OPTIONS] COMMAND ...
```

| Option | Description |
|--------|-------------|
| `--version` | Print version and exit |
| `-h`, `--help` | Show help |
| `--pypdf-strict` / `--no-pypdf-strict` | Pass `strict=True` to pypdf readers (default: **off**, `strict=False`) |
| `-v`, `--verbose` | Log steps to stderr |

## Commands

### compress

Reduce PDF size toward a target percentage of the original file size (best-effort).

```bash
vwpdfutils compress report.pdf report_small.pdf
vwpdfutils compress report.pdf report_small.pdf --ratio 30
```

- Default `--ratio`: **50** (target ~50% of original bytes)
- `--password` for encrypted inputs

### concat

Merge entire PDFs in CLI order (no per-file page ranges in v1).

```bash
vwpdfutils concat -o merged.pdf part1.pdf part2.pdf part3.pdf
```

- `--password` applies to all encrypted inputs

### booklet

Saddle-stitch 2-up imposition for duplex printing.

```bash
vwpdfutils booklet doc.pdf doc_booklet.pdf
vwpdfutils booklet doc.pdf doc_booklet.pdf --paper a4 --binding left
```

- `--paper`: `letter` (612×792 pt) or `a4` (595×842 pt); default `letter`
- `--binding`: `left` or `right`
- `--pad`: `auto`, `yes`, or `no` (pad to multiple of 4 pages)

### split

Remove pages; output keeps remaining pages in order.

Page ranges are **1-based**: `3`, `2-5`, `1,3,5-7`, `all`, `*`.

```bash
vwpdfutils split input.pdf output.pdf --remove 1
vwpdfutils split input.pdf output.pdf --remove 2-4,10
```

`--pages` is an alias for `--remove`.

### rotate

Rotate pages **clockwise**; v1 supports multiples of 90° only.

```bash
vwpdfutils rotate scan.pdf scan_fixed.pdf --angle 90 --pages 1
vwpdfutils rotate doc.pdf doc_rotated.pdf --angle 180 --pages all
```

- `--angle` required (1–360; must be multiple of 90)
- `--pages` default: `all`
- `--password` for encrypted inputs

### convert2pdf

One output page per input file, in order.

```bash
vwpdfutils convert2pdf -o album.pdf cover.png diagram.pdf notes.txt
```

- PDF inputs: **first page only**
- Images: PNG, JPEG, TIFF, BMP, GIF
- Text: `.txt` (word-wrapped, one page)
- Default page size: US Letter (612×792 pt)

## Testing

```bash
pytest
pytest --cov=vwpdfutils --cov-report=term-missing
```

## Limits (v1)

- Practical guidance: ~500 pages, ~100 MB per file on typical desktops
- No digital signatures, OCR, form filling, folder globbing, or GUI
- Output overwrites existing files (verbose mode warns)

## Booklet print check (manual)

1. Create a 4- or 8-page test PDF with page numbers visible.
2. Run `vwpdfutils booklet doc.pdf doc_booklet.pdf`.
3. Print duplex (flip on long edge), fold, and confirm page order reads 1…N.

## Documentation

- [spec.md](./spec.md) — functional requirements
- [plan.md](./plan.md) — implementation plan
- [tasks_checklist.md](./tasks_checklist.md) — implementation checklist
