"""Tests for root CLI global options."""

from __future__ import annotations

from typer.testing import CliRunner

from vwpdfutils.cli import app
from vwpdfutils.context import CliContext


runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_help_lists_six_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for name in ("compress", "concat", "booklet", "split", "rotate", "convert2pdf"):
        assert name in result.stdout


def test_pypdf_strict_in_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "pypdf-strict" in result.stdout
