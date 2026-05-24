"""Tests for booklet imposition order."""

from __future__ import annotations

import pytest

from vwpdfutils._internal.imposition import (
    apply_binding,
    booklet_sheet_sequence,
    pad_page_count,
    saddle_stitch_pairs,
)


def test_pad_page_count() -> None:
    assert pad_page_count(1, "auto") == 4
    assert pad_page_count(4, "auto") == 4
    assert pad_page_count(5, "yes") == 8
    assert pad_page_count(5, "no") == 5


def test_saddle_stitch_n4() -> None:
    assert saddle_stitch_pairs(4) == [(4, 1), (2, 3)]
    assert booklet_sheet_sequence(4) == [4, 1, 2, 3]


def test_saddle_stitch_n8() -> None:
    assert saddle_stitch_pairs(8) == [(8, 1), (2, 7), (6, 3), (4, 5)]
    assert booklet_sheet_sequence(8) == [8, 1, 2, 7, 6, 3, 4, 5]


def test_saddle_stitch_n12() -> None:
    pairs = saddle_stitch_pairs(12)
    assert len(pairs) == 6
    assert pairs[0] == (12, 1)
    assert pairs[-1] == (6, 7)


def test_right_binding_swaps_pairs() -> None:
    left_pairs = saddle_stitch_pairs(4)
    right_pairs = apply_binding(left_pairs, "right")
    assert right_pairs == [(1, 4), (3, 2)]


def test_invalid_page_count() -> None:
    with pytest.raises(ValueError):
        saddle_stitch_pairs(3)
