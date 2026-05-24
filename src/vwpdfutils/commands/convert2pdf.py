"""convert2pdf — build a PDF with one page per input file."""

from __future__ import annotations

import io
import textwrap
from pathlib import Path
from typing import Annotated

import typer
from pypdf import PageObject, PdfReader
from PIL import Image, ImageDraw, ImageFont

from vwpdfutils.context import CliContext, log
from vwpdfutils.errors import cli_error, handle_pdf_error, warn_overwrite
from vwpdfutils.pdf_io import (
    atomic_write_pdf,
    create_writer,
    open_reader,
    validate_input_file,
)

_HELP = "Convert files to a single PDF (one page per input, in order)."

LETTER_WIDTH = 612.0
LETTER_HEIGHT = 792.0
MARGIN_PT = 36.0

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif"}
TEXT_EXTENSIONS = {".txt"}
PDF_EXTENSION = ".pdf"

SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS | TEXT_EXTENSIONS | {PDF_EXTENSION}


def register(parent: typer.Typer) -> None:
    parent.command(name="convert2pdf", help=_HELP)(convert2pdf_cmd)


def _content_area() -> tuple[float, float]:
    width = LETTER_WIDTH - 2 * MARGIN_PT
    height = LETTER_HEIGHT - 2 * MARGIN_PT
    return width, height


def _pil_page_to_pdf_page(image: Image.Image) -> PageObject:
    """Rasterize a Pillow image to a single PDF page via Pillow's PDF backend."""
    buffer = io.BytesIO()
    image.save(buffer, format="PDF", resolution=72.0)
    buffer.seek(0)
    reader = PdfReader(buffer)
    if len(reader.pages) == 0:
        cli_error("Error: failed to render page from image.")
    return reader.pages[0]


def _fit_image_on_letter(img: Image.Image) -> Image.Image:
    """Scale image to fit letter page content area, centered on white canvas."""
    content_w, content_h = _content_area()
    img = img.convert("RGB")
    scale = min(content_w / img.width, content_h / img.height)
    new_w = max(1, int(img.width * scale))
    new_h = max(1, int(img.height * scale))
    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

    canvas = Image.new(
        "RGB",
        (int(LETTER_WIDTH), int(LETTER_HEIGHT)),
        "white",
    )
    x_offset = int(MARGIN_PT + (content_w - new_w) / 2)
    y_offset = int(MARGIN_PT + (content_h - new_h) / 2)
    canvas.paste(img, (x_offset, y_offset))
    return canvas


def _image_to_pdf_page(image_path: Path) -> PageObject:
    with Image.open(image_path) as img:
        return _pil_page_to_pdf_page(_fit_image_on_letter(img))


def _text_to_pdf_page(text_path: Path) -> PageObject:
    content_w, content_h = _content_area()
    text = text_path.read_text(encoding="utf-8", errors="replace")
    chars_per_line = max(20, int(content_w / 7))
    wrapped = textwrap.fill(text, width=chars_per_line)

    image = Image.new("RGB", (int(content_w), int(content_h)), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("cour.ttf", size=12)
    except OSError:
        font = ImageFont.load_default()
    draw.multiline_text((8, 8), wrapped, fill="black", font=font)
    return _pil_page_to_pdf_page(_fit_image_on_letter(image))


def _pdf_first_page(input_path: Path, cli_ctx: CliContext) -> PageObject:
    reader = open_reader(input_path, cli_ctx)
    if len(reader.pages) == 0:
        cli_error(f"Error: PDF has no pages: {input_path}")
    return reader.pages[0]


def _convert_file(input_path: Path, cli_ctx: CliContext) -> PageObject:
    validate_input_file(input_path)
    suffix = input_path.suffix.lower()

    if suffix == PDF_EXTENSION:
        return _pdf_first_page(input_path, cli_ctx)
    if suffix in IMAGE_EXTENSIONS:
        return _image_to_pdf_page(input_path)
    if suffix in TEXT_EXTENSIONS:
        return _text_to_pdf_page(input_path)

    allowed = ", ".join(sorted(ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS))
    cli_error(
        f"Error: unsupported format {suffix!r} for {input_path.name}. "
        f"Allowed types: {allowed}."
    )
    raise AssertionError("unreachable")


def convert2pdf_cmd(
    ctx: typer.Context,
    output: Annotated[
        Path,
        typer.Option("-o", "--output", help="Output PDF path."),
    ],
    inputs: Annotated[
        list[Path],
        typer.Argument(help="Input files (one output page each, in order)."),
    ],
) -> None:
    """
  Each input file becomes exactly one page in the output PDF.

  PDF inputs contribute the first page only. Images and plain text are supported.

  Default page size is US Letter (612×792 pt).

  Examples:

    vwpdfutils convert2pdf -o album.pdf cover.png diagram.pdf notes.txt
    """
    cli_ctx: CliContext = ctx.obj
    if not inputs:
        typer.echo("Error: at least one input file is required.", err=True)
        raise typer.Exit(2)

    if output.exists():
        warn_overwrite(cli_ctx.verbose, str(output))

    try:
        writer = create_writer(cli_ctx)
        for input_path in inputs:
            page = _convert_file(input_path, cli_ctx)
            writer.add_page(page)
            log(cli_ctx, f"added page from {input_path}")

        atomic_write_pdf(writer, output)
        typer.echo(f"Wrote {output} ({len(inputs)} page(s))")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
