"""Tests for pdf_io helpers."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pypdf import PdfReader, PdfWriter

from vwpdfutils.context import CliContext
from vwpdfutils.pdf_io import (
    atomic_write_pdf,
    create_writer,
    ensure_parent_dir,
    open_reader,
    validate_input_file,
)


def test_atomic_write_creates_parent_and_valid_pdf(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "out" / "result.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    atomic_write_pdf(writer, output)
    assert output.is_file()
    assert len(PdfReader(output).pages) == 1
    assert not output.with_suffix(".pdf.tmp").exists()


def test_ensure_parent_dir(tmp_path: Path) -> None:
    target = tmp_path / "a" / "b" / "c.pdf"
    ensure_parent_dir(target)
    assert target.parent.is_dir()


def test_validate_input_file_rejects_directory(tmp_path: Path) -> None:
    import typer

    with pytest.raises(typer.Exit):
        validate_input_file(tmp_path)


def test_open_reader_strict_flag(tmp_path: Path, one_page_pdf: Path) -> None:
    ctx = CliContext(pypdf_strict=True)
    with patch("vwpdfutils.pdf_io.PdfReader") as mock_reader:
        mock_reader.return_value.is_encrypted = False
        mock_reader.return_value.pages = [object()]
        open_reader(one_page_pdf, ctx)
        mock_reader.assert_called_once()
        assert mock_reader.call_args.kwargs["strict"] is True


def test_atomic_write_removes_temp_on_failure(tmp_path: Path) -> None:
    output = tmp_path / "fail.pdf"
    writer = create_writer(CliContext())
    with patch.object(writer, "write", side_effect=OSError("disk full")):
        with pytest.raises(OSError):
            atomic_write_pdf(writer, output)
    assert not output.with_suffix(".pdf.tmp").exists()
