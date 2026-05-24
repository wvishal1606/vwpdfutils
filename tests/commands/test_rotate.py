"""Tests for rotate command."""

from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader
from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf, read_page_count

runner = CliRunner()


def test_rotate_page_one_only(tmp_path: Path, two_page_pdf: Path) -> None:
    output = tmp_path / "rotated.pdf"
    result = runner.invoke(
        app,
        ["rotate", str(two_page_pdf), str(output), "--angle", "90", "--pages", "1"],
    )
    assert result.exit_code == 0
    reader = PdfReader(output)
    assert reader.pages[0].get("/Rotate", 0) in (90, -270, 270)
    assert reader.pages[1].get("/Rotate", 0) in (0, None) or reader.pages[1].get("/Rotate", 0) == 0


def test_rotate_all_pages(two_page_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "rotated.pdf"
    result = runner.invoke(
        app,
        ["rotate", str(two_page_pdf), str(output), "--angle", "180"],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_rotate_rejects_invalid_angles(one_page_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "out.pdf"
    for angle in ("0", "361", "45"):
        result = runner.invoke(
            app,
            ["rotate", str(one_page_pdf), str(output), "--angle", angle],
        )
        assert result.exit_code != 0, f"angle {angle} should fail"
