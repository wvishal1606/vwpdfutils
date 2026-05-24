"""Centralized PDF I/O — all PdfReader/PdfWriter construction goes through here."""

from __future__ import annotations

import os
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from vwpdfutils.context import CliContext
from vwpdfutils.errors import cli_error, handle_pdf_error


def validate_input_file(path: Path) -> None:
    """Ensure path exists, is a regular file, and is readable."""
    if path.is_dir():
        cli_error(f"Error: expected a file, got directory: {path}")
    if not path.is_file():
        cli_error(f"Error: file not found: {path}")
    if not os.access(path, os.R_OK):
        cli_error(f"Error: file is not readable: {path}")


def validate_pdf_file(path: Path) -> None:
    """Validate file exists and has a .pdf extension (case-insensitive)."""
    validate_input_file(path)
    if path.suffix.lower() != ".pdf":
        cli_error(f"Error: not a PDF file: {path}")


def ensure_parent_dir(output_path: Path) -> None:
    """Create parent directories for output_path if missing."""
    parent = output_path.parent
    if parent and not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)


def open_reader(
    path: Path,
    ctx: CliContext,
    password: str | None = None,
) -> PdfReader:
    """Open a PDF for reading with global strict setting."""
    validate_input_file(path)
    try:
        reader = PdfReader(
            stream=str(path),
            strict=ctx.pypdf_strict,
        )
        if reader.is_encrypted:
            if password is None:
                cli_error(
                    "Error: PDF is encrypted. Provide --password to open it.",
                )
            decrypt_result = reader.decrypt(password)
            if decrypt_result == 0:
                cli_error("Error: incorrect PDF password.")
        return reader
    except Exception as exc:
        handle_pdf_error(exc)
        raise  # unreachable; handle_pdf_error always exits


def create_writer(ctx: CliContext) -> PdfWriter:
    """Create a PdfWriter with global strict setting."""
    return PdfWriter()


def atomic_write_pdf(writer: PdfWriter, output_path: Path) -> None:
    """Write PDF atomically via temp file in destination directory."""
    ensure_parent_dir(output_path)
    temp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    try:
        with open(temp_path, "wb") as stream:
            writer.write(stream)
        temp_path.replace(output_path)
    except Exception:
        if temp_path.exists():
            temp_path.unlink(missing_ok=True)
        raise
