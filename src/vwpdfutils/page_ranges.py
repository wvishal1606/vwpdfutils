"""Parse 1-based page range expressions into 0-based indices."""

from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"^(\d+)(?:-(\d+))?$")


def parse_page_spec(spec: str, page_count: int) -> list[int]:
    """
    Parse a page range expression into sorted unique 0-based indices.

    Supports: single page (3), range (2-5), comma lists (1,3,5-7), all, *.
    """
    if page_count < 1:
        raise ValueError("document has no pages")

    spec = spec.strip()
    if not spec:
        raise ValueError("page specification is empty")

    if spec.lower() in ("all", "*"):
        return list(range(page_count))

    indices: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            raise ValueError("empty segment in page specification")

        match = _TOKEN_RE.match(part)
        if not match:
            raise ValueError(f"invalid page specification segment: {part!r}")

        start_str, end_str = match.groups()
        start = int(start_str)
        end = int(end_str) if end_str is not None else start

        if start < 1:
            raise ValueError(
                f"page number must be >= 1 (got {start}); document has {page_count} page(s)"
            )
        if end < start:
            raise ValueError(
                f"invalid range {start}-{end}: start must be <= end; "
                f"document has {page_count} page(s)"
            )
        if end > page_count:
            raise ValueError(
                f"page {end} out of range; document has {page_count} page(s)"
            )

        for page_num in range(start, end + 1):
            indices.add(page_num - 1)

    return sorted(indices)


def format_page_indices(indices: list[int]) -> str:
    """Format 0-based indices as 1-based comma-separated list for messages."""
    return ", ".join(str(i + 1) for i in indices)
