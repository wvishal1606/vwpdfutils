"""Shared pytest fixtures."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from pypdf import PdfReader, PdfWriter


@pytest.fixture
def tmp_pdf_dir(tmp_path: Path) -> Path:
    return tmp_path


def make_pdf(path: Path, page_count: int = 1, text: str | None = None) -> Path:
    """Write a minimal PDF with the given number of pages."""
    del text  # reserved for future labeled fixtures
    writer = PdfWriter()
    for _ in range(page_count):
        writer.add_blank_page(width=612, height=792)
    with open(path, "wb") as stream:
        writer.write(stream)
    return path


@pytest.fixture
def one_page_pdf(tmp_path: Path) -> Path:
    return make_pdf(tmp_path / "one.pdf", 1, "page")


@pytest.fixture
def two_page_pdf(tmp_path: Path) -> Path:
    return make_pdf(tmp_path / "two.pdf", 2, "page")


@pytest.fixture
def three_page_pdf(tmp_path: Path) -> Path:
    return make_pdf(tmp_path / "three.pdf", 3, "page")


@pytest.fixture
def four_page_pdf(tmp_path: Path) -> Path:
    return make_pdf(tmp_path / "four.pdf", 4, "page")


@pytest.fixture
def empty_pdf(tmp_path: Path) -> Path:
    path = tmp_path / "empty.pdf"
    writer = PdfWriter()
    with open(path, "wb") as stream:
        writer.write(stream)
    return path


@pytest.fixture
def pdf_bytes_one_page() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def read_page_count(path: Path) -> int:
    return len(PdfReader(path).pages)
