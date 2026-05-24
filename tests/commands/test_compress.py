"""Tests for compress command."""

from __future__ import annotations

from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from typer.testing import CliRunner

from vwpdfutils.cli import app
from tests.conftest import make_pdf

runner = CliRunner()


def _pdf_with_image(path: Path, *, rgba: bool = False) -> Path:
    """Minimal single-page PDF with an embedded raster image."""
    png_path = path.with_suffix(".png")
    if rgba:
        img = Image.new("RGBA", (400, 300), (0, 0, 0, 0))
        for x in range(120, 280):
            for y in range(100, 200):
                img.putpixel((x, y), (128, 0, 200, 255))
    else:
        img = Image.new("RGB", (400, 300), color="blue")
    img.save(png_path)
    image_pdf = path.with_suffix(".img.pdf")
    Image.open(png_path).save(image_pdf, format="PDF", resolution=72.0)
    png_path.unlink(missing_ok=True)
    return image_pdf


def test_compress_default_ratio_50(tmp_path: Path, one_page_pdf: Path) -> None:
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["compress", str(one_page_pdf), str(output)],
    )
    assert result.exit_code == 0
    assert output.is_file()
    assert len(PdfReader(output).pages) >= 1


def test_compress_invalid_ratio(one_page_pdf: Path, tmp_path: Path) -> None:
    output = tmp_path / "out.pdf"
    for ratio in ("0", "101"):
        result = runner.invoke(
            app,
            ["compress", str(one_page_pdf), str(output), "--ratio", ratio],
        )
        assert result.exit_code != 0


def test_compress_output_valid(tmp_path: Path) -> None:
    source = make_pdf(tmp_path / "big.pdf", 3)
    output = tmp_path / "small.pdf"
    result = runner.invoke(
        app,
        ["compress", str(source), str(output), "--ratio", "80"],
    )
    assert result.exit_code == 0
    assert output.stat().st_size > 0


def test_compress_flattens_transparency_to_white(tmp_path: Path) -> None:
    """Transparent areas must not become black after compression."""
    from vwpdfutils._internal.compression import _flatten_transparency

    rgba = Image.new("RGBA", (50, 50), (0, 0, 0, 0))
    for x in range(50):
        for y in range(50):
            if 15 < x < 35 and 15 < y < 35:
                rgba.putpixel((x, y), (200, 50, 50, 255))
    flat = _flatten_transparency(rgba)
    assert flat.mode == "RGB"
    assert flat.getpixel((0, 0)) == (255, 255, 255)
    assert flat.getpixel((25, 25)) == (200, 50, 50)


def test_compress_image_pdf_strict_readable(tmp_path: Path) -> None:
    """Compressed image PDFs must remain structurally valid (Acrobat-safe)."""
    source = _pdf_with_image(tmp_path / "source.pdf")
    output = tmp_path / "compressed.pdf"
    result = runner.invoke(
        app,
        ["compress", str(source), str(output), "--ratio", "50"],
    )
    assert result.exit_code == 0
    reader = PdfReader(output, strict=True)
    assert len(reader.pages) >= 1
    for page in reader.pages:
        list(page.images)


def test_compress_rgba_image_pdf(tmp_path: Path) -> None:
    source = _pdf_with_image(tmp_path / "rgba.pdf", rgba=True)
    output = tmp_path / "out.pdf"
    result = runner.invoke(
        app,
        ["compress", str(source), str(output), "--ratio", "50"],
    )
    assert result.exit_code == 0
    reader = PdfReader(output, strict=True)
    for image_file in reader.pages[0].images:
        corner = image_file.image.convert("RGB").getpixel((0, 0))
        assert corner == (255, 255, 255), f"transparent corner became {corner}"
