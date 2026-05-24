"""Tests for booklet command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf, read_page_count

runner = CliRunner()


def test_booklet_four_pages(tmp_path: Path, four_page_pdf: Path) -> None:
    output = tmp_path / "booklet.pdf"
    result = runner.invoke(
        app,
        ["booklet", str(four_page_pdf), str(output)],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_booklet_one_page_pads_to_four(tmp_path: Path, one_page_pdf: Path) -> None:
    output = tmp_path / "booklet.pdf"
    result = runner.invoke(
        app,
        ["booklet", str(one_page_pdf), str(output), "--pad", "auto"],
    )
    assert result.exit_code == 0
    assert read_page_count(output) == 2


def test_booklet_binding_option(tmp_path: Path, four_page_pdf: Path) -> None:
    left_out = tmp_path / "left.pdf"
    right_out = tmp_path / "right.pdf"
    r1 = runner.invoke(
        app,
        ["booklet", str(four_page_pdf), str(left_out), "--binding", "left"],
    )
    r2 = runner.invoke(
        app,
        ["booklet", str(four_page_pdf), str(right_out), "--binding", "right"],
    )
    assert r1.exit_code == 0
    assert r2.exit_code == 0
    assert left_out.stat().st_size > 0
    assert right_out.stat().st_size > 0
