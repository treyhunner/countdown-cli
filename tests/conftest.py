"""PyTest configuration."""

from _pytest.assertion import truncate

truncate.DEFAULT_MAX_LINES = 40
truncate.DEFAULT_MAX_CHARS = 40 * 80


def pytest_assertrepr_compare(
    op,
    left,
    right,
):  # pragma: nocover
    if (
        isinstance(left, str)
        and isinstance(right, str)
        and "█" in right
        and op == "=="
    ):
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
