"""Tests for concat command."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf, read_page_count

runner = CliRunner()


def test_concat_two_one_page_pdfs(tmp_path: Path, one_page_pdf: Path) -> None:
    second = make_pdf(tmp_path / "second.pdf", 1)
    output = tmp_path / "merged.pdf"
    result = runner.invoke(
        app,
        ["concat", "-o", str(output), str(one_page_pdf), str(second)],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_concat_missing_input(tmp_path: Path) -> None:
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["concat", "-o", str(output), str(tmp_path / "missing.pdf")],
    )
    assert result.exit_code != 0


def test_concat_empty_pdf_allowed(tmp_path: Path, empty_pdf: Path, one_page_pdf: Path) -> None:
    output = tmp_path / "merged.pdf"
    result = runner.invoke(
        app,
        ["concat", "-o", str(output), str(empty_pdf), str(one_page_pdf)],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 1
