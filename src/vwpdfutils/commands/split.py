"""split — remove specified pages from a PDF."""

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

_HELP = "Remove pages from a PDF; output contains remaining pages in order."


def register(parent: typer.Typer) -> None:
    parent.command(name="split", help=_HELP)(split_cmd)


def split_cmd(
    ctx: typer.Context,
    input_pdf: Annotated[Path, typer.Argument(help="Source PDF path.")],
    output_pdf: Annotated[Path, typer.Argument(help="Output PDF path.")],
    remove: Annotated[
        str | None,
        typer.Option(
            "--remove",
            "--pages",
            help="Pages to remove (1-based): e.g. 3, 2-5, 1,3,5-7, all, *.",
        ),
    ] = None,
) -> None:
    """
  Remove the given pages; all other pages are copied in original order.

  Page numbers are 1-based. Use commas and ranges (see global page-range syntax).

  Examples:

    vwpdfutils split input.pdf output.pdf --remove 1
    vwpdfutils split input.pdf output.pdf --remove 2-4,10
    """
    cli_ctx: CliContext = ctx.obj
    if remove is None:
        typer.echo("Error: --remove (or --pages) is required.", err=True)
        raise typer.Exit(2)

    if output_pdf.exists():
        warn_overwrite(cli_ctx.verbose, str(output_pdf))

    try:
        validate_pdf_file(input_pdf)
        reader = open_reader(input_pdf, cli_ctx)
        page_count = len(reader.pages)
        if page_count == 0:
            cli_error("Error: input PDF has no pages.")

        try:
            remove_indices = parse_page_spec(remove, page_count)
        except ValueError as exc:
            cli_error(f"Error: {exc}")

        if not remove_indices:
            cli_error("Error: remove set is empty.")

        keep_indices = [i for i in range(page_count) if i not in set(remove_indices)]
        if not keep_indices:
            cli_error("Error: cannot remove all pages; at least one page must remain.")

        writer = create_writer(cli_ctx)
        for index in keep_indices:
            writer.add_page(reader.pages[index])

        atomic_write_pdf(writer, output_pdf)
        log(cli_ctx, f"removed {len(remove_indices)} page(s); kept {len(keep_indices)}")
        typer.echo(f"Wrote {output_pdf} ({len(keep_indices)} page(s))")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
