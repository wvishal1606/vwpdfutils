"""Tests for split command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import read_page_count

runner = CliRunner()


def test_split_remove_first_page(tmp_path: Path, three_page_pdf: Path) -> None:
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["split", str(three_page_pdf), str(output), "--remove", "1"],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_split_remove_range(tmp_path: Path) -> None:
    from tests.conftest import make_pdf

    source = make_pdf(tmp_path / "ten.pdf", 10)
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["split", str(source), str(output), "--remove", "2-4,10"],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 6


def test_split_remove_all_pages_error(three_page_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["split", str(three_page_pdf), str(output), "--remove", "all"],
    )
    assert result.exit_code != 0
