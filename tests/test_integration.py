"""Integration and edge-case tests."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf

runner = CliRunner()


def test_corrupt_pdf_fails(tmp_path: Path) -> None:
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a pdf at all")
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["split", str(bad), str(output), "--remove", "1"],
    )
    assert result.exit_code != 0
    assert result.stderr


def test_verbose_mode(tmp_path: Path, one_page_pdf: Path) -> None:
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        [
            "-v",
            "compress",
            str(one_page_pdf),
            str(output),
        ],
    )
    assert result.exit_code == 0


def test_path_with_spaces(tmp_path: Path, one_page_pdf: Path) -> None:
    spaced = tmp_path / "my docs"
    spaced.mkdir()
    output = spaced / "out file.pdf"
    result = runner.invoke(
        app,
        ["concat", "-o", str(output), str(one_page_pdf)],
    )
    assert result.exit_code == 0
    assert output.is_file()
