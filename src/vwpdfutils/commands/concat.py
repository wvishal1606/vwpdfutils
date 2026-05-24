"""concat — merge multiple PDFs in CLI order."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vwpdfutils.context import CliContext, log
from vwpdfutils.errors import handle_pdf_error, warn_overwrite
from vwpdfutils.pdf_io import atomic_write_pdf, create_writer, open_reader, validate_pdf_file

_HELP = "Merge multiple PDFs into one file, preserving page order."


def register(parent: typer.Typer) -> None:
    parent.command(name="concat", help=_HELP)(concat_cmd)


def concat_cmd(
    ctx: typer.Context,
    output: Annotated[
        Path,
        typer.Option(
            "-o",
            "--output",
            help="Output PDF path.",
        ),
    ],
    inputs: Annotated[
        list[Path],
        typer.Argument(help="Input PDF paths, merged in listed order."),
    ],
    password: Annotated[
        str | None,
        typer.Option("--password", help="Password for encrypted inputs (same for all)."),
    ] = None,
) -> None:
    """
  Merge entire PDF files in the order given on the command line.

  Per-file page ranges are not supported in v1; each input contributes all pages.

  Examples:

    vwpdfutils concat -o merged.pdf part1.pdf part2.pdf part3.pdf
    """
    cli_ctx: CliContext = ctx.obj
    if not inputs:
        typer.echo("Error: at least one input PDF is required.", err=True)
        raise typer.Exit(2)

    if output.exists():
        warn_overwrite(cli_ctx.verbose, str(output))

    try:
        writer = create_writer(cli_ctx)
        total_pages = 0
        for index, input_path in enumerate(inputs):
            validate_pdf_file(input_path)
            reader = open_reader(input_path, cli_ctx, password=password)
            if index == 0 and reader.metadata:
                writer.add_metadata(reader.metadata)
            writer.append(reader)
            page_count = len(reader.pages)
            total_pages += page_count
            log(cli_ctx, f"merged {input_path} ({page_count} page(s))")

        atomic_write_pdf(writer, output)
        log(cli_ctx, f"total pages: {total_pages}")
        typer.echo(f"Wrote {output} ({total_pages} page(s))")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
