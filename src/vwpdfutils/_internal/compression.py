"""Iterative PDF compression toward a target file size."""

from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader, PdfWriter

from vwpdfutils.context import CliContext
from vwpdfutils.pdf_io import create_writer, open_reader

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    Image = None  # type: ignore[misc, assignment]

_QUALITY_STEPS = (85, 75, 65, 55, 45, 35, 25)
_SCALE_STEPS = (1.0, 0.85, 0.7, 0.55, 0.45)


def _writer_to_bytes(writer: PdfWriter) -> bytes:
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _has_images(writer: PdfWriter) -> bool:
    for page in writer.pages:
        if page.images:
            return True
    return False


def _flatten_transparency(
    pil_image: Image.Image,
    background: tuple[int, int, int] = (255, 255, 255),
) -> Image.Image:
    """
    Composite transparent pixels onto a solid background.

    Converting RGBA/LA/P-with-transparency directly to RGB fills alpha with black;
  use this before JPEG or PDF re-encode so badges/icons keep a white backdrop.
    """
    if pil_image.mode == "P" and pil_image.info.get("transparency") is not None:
        pil_image = pil_image.convert("RGBA")
    elif pil_image.mode == "P":
        return pil_image.convert("RGB")

    if pil_image.mode == "LA":
        pil_image = pil_image.convert("RGBA")

    if pil_image.mode == "RGBA":
        base = Image.new("RGBA", pil_image.size, (*background, 255))
        return Image.alpha_composite(base, pil_image).convert("RGB")

    if pil_image.mode == "RGB":
        return pil_image
    if pil_image.mode == "L":
        return pil_image.convert("RGB")
    if pil_image.mode == "CMYK":
        return pil_image.convert("RGB")
    return pil_image.convert("RGB")


def _apply_image_compression(
    writer: PdfWriter,
    quality: int,
    scale: float,
) -> None:
    """Re-encode embedded images via pypdf ImageFile.replace (preserves PDF structure)."""
    if Image is None:
        return

    for page in writer.pages:
        for image_file in page.images:
            try:
                pil_image = image_file.image
                if scale < 1.0:
                    new_w = max(1, int(pil_image.width * scale))
                    new_h = max(1, int(pil_image.height * scale))
                    pil_image = pil_image.resize(
                        (new_w, new_h),
                        Image.Resampling.LANCZOS,
                    )
                pil_image = _flatten_transparency(pil_image)
                image_file.replace(pil_image, quality=quality)
            except Exception:
                continue


def _finalize_writer(writer: PdfWriter) -> None:
    """Lossless stream compression and object deduplication (call before write)."""
    for page in writer.pages:
        try:
            page.compress_content_streams()
        except Exception:
            pass
    writer.compress_identical_objects(
        remove_identicals=True,
        remove_orphans=True,
    )


def _build_writer(
    input_path: Path,
    ctx: CliContext,
    password: str | None,
    quality: int | None,
    scale: float,
) -> PdfWriter:
    reader = open_reader(input_path, ctx, password=password)
    writer = create_writer(ctx)
    writer.append(reader)
    if quality is not None and _has_images(writer):
        _apply_image_compression(writer, quality, scale)
    _finalize_writer(writer)
    return writer


def compress_pdf(
    input_path: Path,
    ctx: CliContext,
    target_size: int,
    password: str | None = None,
) -> tuple[PdfWriter, int]:
    """
    Build a compressed PdfWriter and return (writer, best_byte_size).

    Best-effort toward target_size; may not reach exact ratio.
    """
    best_writer = _build_writer(input_path, ctx, password, quality=None, scale=1.0)
    best_size = len(_writer_to_bytes(best_writer))

    if best_size <= target_size:
        return best_writer, best_size

    probe = _build_writer(input_path, ctx, password, quality=None, scale=1.0)
    if not _has_images(probe):
        return best_writer, best_size

    for scale in _SCALE_STEPS:
        for quality in _QUALITY_STEPS:
            trial_writer = _build_writer(
                input_path,
                ctx,
                password,
                quality=quality,
                scale=scale,
            )
            size = len(_writer_to_bytes(trial_writer))
            if size < best_size:
                best_size = size
                best_writer = trial_writer
            if size <= target_size:
                return trial_writer, size

    return best_writer, best_size
