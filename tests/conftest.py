"""PyTest configuration."""
from __future__ import annotations

from typing import Any

from _pytest.assertion import truncate

truncate.DEFAULT_MAX_LINES = 40
truncate.DEFAULT_MAX_CHARS = 40 * 80


def pytest_assertrepr_compare(
    op: str,
    left: Any,
    right: Any,
) -> list[str] | None:  # pragma: nocover
    if isinstance(left, str) and isinstance(right, str) and "█" in right and op == "==":
        return [
            "Big number string comparison doesn't match",
            "Got:",
            *left.splitlines(),
            "Expected:",
            *right.splitlines(),
            "",
            f"Repr Comparison: {left!r} != {right!r}",
        ]
    return None
