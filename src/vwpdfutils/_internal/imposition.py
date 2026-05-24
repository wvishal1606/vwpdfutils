"""Saddle-stitch booklet page pairing for duplex printing."""

from __future__ import annotations


def pad_page_count(n: int, pad_mode: str) -> int:
    """Return target page count padded to multiple of 4 when pad_mode allows."""
    if pad_mode == "no":
        return n
    if n % 4 == 0:
        return n
    if pad_mode in ("auto", "yes"):
        return n + (4 - n % 4)
    raise ValueError(f"invalid pad mode: {pad_mode!r}")


def saddle_stitch_pairs(page_count: int) -> list[tuple[int, int]]:
    """
    Return (left, right) 1-based page pairs for each imposed output sheet.

    Each tuple is one 2-up output page (left and right logical pages).
    page_count must be a positive multiple of 4.
    """
    if page_count < 4 or page_count % 4 != 0:
        raise ValueError(
            f"page count must be a positive multiple of 4, got {page_count}"
        )

    pairs: list[tuple[int, int]] = []
    num_sheet_groups = page_count // 4

    for sheet_index in range(num_sheet_groups):
        front_left = page_count - 2 * sheet_index
        front_right = 1 + 2 * sheet_index
        back_left = 2 + 2 * sheet_index
        back_right = page_count - 1 - 2 * sheet_index
        pairs.append((front_left, front_right))
        pairs.append((back_left, back_right))

    return pairs


def apply_binding(
    pairs: list[tuple[int, int]],
    binding: str,
) -> list[tuple[int, int]]:
    """Swap left/right on each pair for right binding."""
    if binding == "left":
        return pairs
    if binding == "right":
        return [(right, left) for left, right in pairs]
    raise ValueError(f"invalid binding: {binding!r}")


def booklet_sheet_sequence(page_count: int) -> list[int]:
    """
    Flattened 1-based page order for imposed output (one entry per half-sheet slot).

    Used by tests to verify imposition order for N=4, 8, 12.
    """
    sequence: list[int] = []
    for left, right in saddle_stitch_pairs(page_count):
        sequence.extend([left, right])
    return sequence
