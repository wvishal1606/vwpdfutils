"""booklet — saddle-stitch 2-up imposition for duplex printing."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from pypdf import PageObject, Transformation

from vwpdfutils._internal.imposition import (
    apply_binding,
    pad_page_count,
    saddle_stitch_pairs,
)
from vwpdfutils.context import CliContext, log
from vwpdfutils.errors import cli_error, handle_pdf_error, warn_overwrite
from vwpdfutils.pdf_io import (
    atomic_write_pdf,
    create_writer,
    open_reader,
    validate_pdf_file,
)

_HELP = "Create a booklet-layout PDF for duplex saddle-stitch printing."

GUTTER_PT = 18.0
MARGIN_PT = 36.0

PAPER_SIZES = {
    "letter": (612.0, 792.0),
    "a4": (595.0, 842.0),
}


class PaperSize(str, Enum):
    letter = "letter"
    a4 = "a4"


class BindingEdge(str, Enum):
    left = "left"
    right = "right"


class PadMode(str, Enum):
    auto = "auto"
    yes = "yes"
    no = "no"


def register(parent: typer.Typer) -> None:
    parent.command(name="booklet", help=_HELP)(booklet_cmd)


def _source_page(
    pages: list[PageObject],
    page_num: int,
    width: float,
    height: float,
) -> PageObject:
    """Return source page or blank placeholder (1-based page_num)."""
    if page_num <= len(pages):
        return pages[page_num - 1]
    return PageObject.create_blank_page(width=width, height=height)


def _fit_transform(
    source: PageObject,
    slot_width: float,
    slot_height: float,
    x_offset: float,
    y_offset: float,
) -> Transformation:
    src_w = float(source.mediabox.width)
    src_h = float(source.mediabox.height)
    scale = min(slot_width / src_w, slot_height / src_h)
    tx = x_offset + (slot_width - src_w * scale) / 2
    ty = y_offset + (slot_height - src_h * scale) / 2
    return (
        Transformation()
        .scale(sx=scale, sy=scale)
        .translate(tx=tx, ty=ty)
    )


def _impose_pair(
    left_page: PageObject,
    right_page: PageObject,
    paper_width: float,
    paper_height: float,
) -> PageObject:
    """Place two logical pages side by side on one output sheet."""
    slot_width = (paper_width - 2 * MARGIN_PT - GUTTER_PT) / 2
    slot_height = paper_height - 2 * MARGIN_PT
    output = PageObject.create_blank_page(width=paper_width, height=paper_height)

    left_tx = _fit_transform(left_page, slot_width, slot_height, MARGIN_PT, MARGIN_PT)
    right_x = MARGIN_PT + slot_width + GUTTER_PT
    right_tx = _fit_transform(
        right_page, slot_width, slot_height, right_x, MARGIN_PT
    )

    output.merge_transformed_page(left_page, left_tx)
    output.merge_transformed_page(right_page, right_tx)
    return output


def booklet_cmd(
    ctx: typer.Context,
    input_pdf: Annotated[Path, typer.Argument(help="Source PDF (single file).")],
    output_pdf: Annotated[Path, typer.Argument(help="Booklet output PDF path.")],
    paper: Annotated[
        PaperSize,
        typer.Option("--paper", help="Sheet size: letter (612×792 pt) or a4."),
    ] = PaperSize.letter,
    binding: Annotated[
        BindingEdge,
        typer.Option("--binding", help="Binding edge (affects left/right placement)."),
    ] = BindingEdge.left,
    pad: Annotated[
        PadMode,
        typer.Option(
            "--pad",
            help="Pad page count to multiple of 4: auto, yes, or no.",
        ),
    ] = PadMode.auto,
) -> None:
    """
  Reorder and impose pages for saddle-stitch duplex printing (2-up per sheet).

  Examples:

    vwpdfutils booklet doc.pdf doc_booklet.pdf
    vwpdfutils booklet doc.pdf doc_booklet.pdf --paper a4 --binding left
    """
    cli_ctx: CliContext = ctx.obj

    if output_pdf.exists():
        warn_overwrite(cli_ctx.verbose, str(output_pdf))

    try:
        validate_pdf_file(input_pdf)
        reader = open_reader(input_pdf, cli_ctx)
        source_pages = list(reader.pages)
        n = len(source_pages)
        if n == 0:
            cli_error("Error: input PDF has no pages.")

        paper_width, paper_height = PAPER_SIZES[paper.value]
        target_count = pad_page_count(n, pad.value)
        log(cli_ctx, f"source pages: {n}; padded target: {target_count}")

        pairs = apply_binding(saddle_stitch_pairs(target_count), binding.value)
        writer = create_writer(cli_ctx)

        for left_num, right_num in pairs:
            left = _source_page(source_pages, left_num, paper_width, paper_height)
            right = _source_page(source_pages, right_num, paper_width, paper_height)
            writer.add_page(_impose_pair(left, right, paper_width, paper_height))

        atomic_write_pdf(writer, output_pdf)
        log(cli_ctx, f"output sheets: {len(pairs)}")
        typer.echo(f"Wrote {output_pdf} ({len(pairs)} sheet(s))")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
