"""CLI context shared across commands."""

from __future__ import annotations

import sys
from dataclasses import dataclass


@dataclass
class CliContext:
    """Global CLI state from root callback."""

    pypdf_strict: bool = False
    verbose: bool = False


def log(ctx: CliContext, message: str) -> None:
    """Write diagnostic message to stderr when verbose mode is enabled."""
    if ctx.verbose:
        print(message, file=sys.stderr)
