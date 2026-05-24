"""rotate — rotate selected pages by a given angle."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vwpdfutils.context import CliContext, log
from vwpdfutils.errors import cli_error, handle_pdf_error, warn_overwrite
from vwpdfutils.page_ranges import parse_page_spec
from vwpdfutils.pdf_io import (
    atomic_write_pdf,
    create_writer,
    open_reader,
    validate_pdf_file,
)

_HELP = "Rotate pages clockwise by a multiple of 90 degrees."


def register(parent: typer.Typer) -> None:
    parent.command(name="rotate", help=_HELP)(rotate_cmd)


def _validate_angle(angle: int) -> None:
    if angle < 1 or angle > 360:
        cli_error("Error: angle must be between 1 and 360 degrees.")
    if angle % 90 != 0:
        cli_error(
            "Error: only multiples of 90° are supported in v1 (90, 180, 270, 360)."
        )


def rotate_cmd(
    ctx: typer.Context,
    input_pdf: Annotated[Path, typer.Argument(help="Source PDF path.")],
    output_pdf: Annotated[Path, typer.Argument(help="Output PDF path.")],
    angle: Annotated[int, typer.Option("--angle", help="Clockwise rotation in degrees (1–360).")],
    pages: Annotated[
        str,
        typer.Option("--pages", help="Pages to rotate (1-based); default: all."),
    ] = "all",
    password: Annotated[
        str | None,
        typer.Option("--password", help="Password for encrypted input."),
    ] = None,
) -> None:
    """
  Rotate selected pages clockwise. Unselected pages are unchanged.

  v1 supports multiples of 90° only (90, 180, 270, 360).

  Examples:

    vwpdfutils rotate scan.pdf scan_fixed.pdf --angle 90 --pages 1
    vwpdfutils rotate doc.pdf doc_rotated.pdf --angle 180 --pages all
    """
    cli_ctx: CliContext = ctx.obj
    _validate_angle(angle)

    if output_pdf.exists():
        warn_overwrite(cli_ctx.verbose, str(output_pdf))

    try:
        validate_pdf_file(input_pdf)
        reader = open_reader(input_pdf, cli_ctx, password=password)
        page_count = len(reader.pages)
        if page_count == 0:
            cli_error("Error: input PDF has no pages.")

        try:
            rotate_indices = set(parse_page_spec(pages, page_count))
        except ValueError as exc:
            cli_error(f"Error: {exc}")

        writer = create_writer(cli_ctx)
        for index in range(page_count):
            page = reader.pages[index]
            if index in rotate_indices:
                page.rotate(angle)
            writer.add_page(page)

        atomic_write_pdf(writer, output_pdf)
        log(cli_ctx, f"rotated {len(rotate_indices)} page(s) by {angle}°")
        typer.echo(f"Wrote {output_pdf}")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
