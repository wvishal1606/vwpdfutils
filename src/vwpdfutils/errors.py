"""User-facing error handling and exit codes."""

from __future__ import annotations

import sys

import typer
from pypdf.errors import PdfReadError


def cli_error(message: str, code: int = 1) -> None:
    """Print message to stderr and exit with the given code."""
    typer.echo(message, err=True)
    raise typer.Exit(code)


def handle_pdf_error(exc: BaseException) -> None:
    """Map PDF and I/O exceptions to actionable stderr messages."""
    if isinstance(exc, FileNotFoundError):
        cli_error(f"Error: file not found: {exc.filename or exc}")
    if isinstance(exc, PdfReadError):
        msg = str(exc).strip() or "cannot read PDF"
        if "password" in msg.lower() or "encrypted" in msg.lower():
            cli_error(
                "Error: PDF is encrypted. Provide --password to open it.",
            )
        cli_error(f"Error: cannot read PDF: {msg}")
    if isinstance(exc, PermissionError):
        cli_error(f"Error: permission denied: {exc}")
    if isinstance(exc, typer.Exit):
        raise
    cli_error(f"Error: {exc}")


def warn_overwrite(ctx_verbose: bool, path: str) -> None:
    """Warn on stderr when overwriting an existing output file."""
    if ctx_verbose:
        print(f"Warning: overwriting existing file: {path}", file=sys.stderr)
