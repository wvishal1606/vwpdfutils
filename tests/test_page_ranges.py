"""Tests for page_ranges.parse_page_spec."""

from __future__ import annotations

import pytest

from vwpdfutils.page_ranges import parse_page_spec


def test_single_page() -> None:
    assert parse_page_spec("3", 5) == [2]


def test_inclusive_range() -> None:
    assert parse_page_spec("2-5", 10) == [1, 2, 3, 4]


def test_comma_list() -> None:
    assert parse_page_spec("1,3,5-7", 10) == [0, 2, 4, 5, 6]


def test_all_and_star() -> None:
    assert parse_page_spec("all", 3) == [0, 1, 2]
    assert parse_page_spec("*", 3) == [0, 1, 2]


def test_out_of_range() -> None:
    with pytest.raises(ValueError, match="out of range"):
        parse_page_spec("11", 10)


def test_invalid_range_start_gt_end() -> None:
    with pytest.raises(ValueError, match="start must be <= end"):
        parse_page_spec("5-3", 10)


def test_page_less_than_one() -> None:
    with pytest.raises(ValueError, match="must be >= 1"):
        parse_page_spec("0", 5)


def test_empty_spec() -> None:
    with pytest.raises(ValueError, match="empty"):
        parse_page_spec("", 5)
