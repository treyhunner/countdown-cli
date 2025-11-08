"""Test cases for the terminal module."""

import sys

from countdown import terminal


def test_check_for_keypress_returns_false_when_not_a_tty():
    """Test that check_for_keypress returns False when not a TTY."""
    # Mock stdin.isatty() to return False
    original_isatty = sys.stdin.isatty
    sys.stdin.isatty = lambda: False

    try:
        result = terminal.check_for_keypress()
        assert result is False, "Should return False when not a TTY"
    finally:
        sys.stdin.isatty = original_isatty
