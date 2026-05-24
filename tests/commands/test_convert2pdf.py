"""Tests for convert2pdf command."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf, read_page_count

runner = CliRunner()


def test_convert_png_and_txt(tmp_path: Path) -> None:
    png_path = tmp_path / "cover.png"
    Image.new("RGB", (100, 80), color="red").save(png_path)
    txt_path = tmp_path / "notes.txt"
    txt_path.write_text("Hello booklet notes.", encoding="utf-8")
    output = tmp_path / "album.pdf"
    result = runner.invoke(
        app,
        ["convert2pdf", "-o", str(output), str(png_path), str(txt_path)],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_convert_pdf_first_page_only(tmp_path: Path) -> None:
    source = make_pdf(tmp_path / "multi.pdf", 3)
    output = tmp_path / "one.pdf"
    result = runner.invoke(
        app,
        ["convert2pdf", "-o", str(output), str(source)],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 1


def test_convert_unsupported_docx(tmp_path: Path) -> None:
    docx = tmp_path / "file.docx"
    docx.write_bytes(b"fake")
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["convert2pdf", "-o", str(output), str(docx)],
    )
    assert result.exit_code != 0
    assert "unsupported" in result.stderr.lower() or "unsupported" in result.stdout.lower()
