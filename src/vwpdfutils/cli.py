"""Root Typer application and global options."""

from __future__ import annotations

import typer

from vwpdfutils import __version__
from vwpdfutils.commands import booklet, compress, concat, convert2pdf, rotate, split
from vwpdfutils.context import CliContext

app = typer.Typer(
    name="vwpdfutils",
    help="PDF utilities: compress, concat, booklet, split, rotate, convert2pdf.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"vwpdfutils {__version__}")
        raise typer.Exit(0)


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
    pypdf_strict: bool = typer.Option(
        False,
        "--pypdf-strict/--no-pypdf-strict",
        help="Pass strict=True to all pypdf readers and writers.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Log processing steps to stderr.",
    ),
) -> None:
    """Global options for vwpdfutils."""
    ctx.obj = CliContext(pypdf_strict=pypdf_strict, verbose=verbose)


compress.register(app)
concat.register(app)
booklet.register(app)
split.register(app)
rotate.register(app)
convert2pdf.register(app)
