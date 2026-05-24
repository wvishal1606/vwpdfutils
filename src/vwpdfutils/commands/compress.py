"""compress — reduce PDF file size toward a target ratio."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from vwpdfutils._internal.compression import compress_pdf
from vwpdfutils.context import CliContext, log
from vwpdfutils.errors import cli_error, handle_pdf_error, warn_overwrite
from vwpdfutils.pdf_io import atomic_write_pdf, validate_pdf_file

_HELP = "Compress a PDF toward a target percentage of original file size."
DEFAULT_RATIO = 50.0


def register(parent: typer.Typer) -> None:
    parent.command(name="compress", help=_HELP)(compress_cmd)


def _validate_ratio(ratio: float) -> None:
    if ratio <= 0 or ratio > 100:
        cli_error("Error: ratio must be greater than 0 and at most 100.")


def compress_cmd(
    ctx: typer.Context,
    input_pdf: Annotated[Path, typer.Argument(help="Source PDF path.")],
    output_pdf: Annotated[Path, typer.Argument(help="Destination PDF path.")],
    ratio: Annotated[
        float,
        typer.Option(
            "--ratio",
            help="Target size as %% of original file size (default: 50).",
        ),
    ] = DEFAULT_RATIO,
    password: Annotated[
        str | None,
        typer.Option("--password", help="Password for encrypted input."),
    ] = None,
) -> None:
    """
  Reduce PDF size toward a target ratio (best-effort).

  --ratio is the target output size as a percentage of the original file size.
  Default is 50 (approximately half the original bytes). Exact size is not guaranteed.

  Examples:

    vwpdfutils compress report.pdf report_small.pdf
    vwpdfutils compress report.pdf report_small.pdf --ratio 30
    """
    cli_ctx: CliContext = ctx.obj
    _validate_ratio(ratio)

    if output_pdf.exists():
        warn_overwrite(cli_ctx.verbose, str(output_pdf))

    try:
        validate_pdf_file(input_pdf)
        original_size = input_pdf.stat().st_size
        target_size = int(original_size * ratio / 100)

        writer, output_size = compress_pdf(
            input_pdf,
            cli_ctx,
            target_size,
            password=password,
        )
        atomic_write_pdf(writer, output_pdf)

        actual_pct = (output_size / original_size * 100) if original_size else 0
        log(
            cli_ctx,
            f"original: {original_size} bytes; output: {output_size} bytes "
            f"({actual_pct:.1f}% of original; target {ratio}%)",
        )
        typer.echo(f"Wrote {output_pdf}")
    except typer.Exit:
        raise
    except Exception as exc:
        handle_pdf_error(exc)
