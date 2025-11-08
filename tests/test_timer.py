"""Test cases for the timer module."""

from textwrap import dedent

import pytest

from countdown import timer
from countdown.digits import CHARS_BY_SIZE


def join_lines(lines):
    """Given list of lines, return string of lines with whitespace stripped."""
    return "\n".join(line.rstrip(" ") for line in lines)


def test_invalid_duration():
    with pytest.raises(ValueError):
        timer.duration("10")


def test_duration_10_seconds():
    assert timer.duration("10s") == 10


def test_duration_60_seconds():
    assert timer.duration("60s") == 60


def test_duration_1_minute():
    assert timer.duration("1m") == 60


def test_duration_10_minutes():
    assert timer.duration("10m") == 600


def test_duration_25_minutes():
    assert timer.duration("25m") == 1500


def test_duration_3_minute_and_30_seconds():
    assert timer.duration("3m30s") == 210


def test_duration_2_minutes_and_8_seconds():
    assert timer.duration("2m8s") == 128


def test_get_number_lines_10_seconds():
    # Use size 5 digits for consistent rendering
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(10, chars)) == dedent(
        """
        ██████ ██████        ██   ██████
        ██  ██ ██  ██  ██   ███   ██  ██
        ██  ██ ██  ██        ██   ██  ██
        ██  ██ ██  ██  ██    ██   ██  ██
        ██████ ██████        ██   ██████
    """
    ).strip("\n")


def test_get_number_lines_60_seconds():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(60, chars)) == dedent(
        """
        ██████   ██        ██████ ██████
        ██  ██  ███    ██  ██  ██ ██  ██
        ██  ██   ██        ██  ██ ██  ██
        ██  ██   ██    ██  ██  ██ ██  ██
        ██████   ██        ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_45_minutes():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(2700, chars)) == dedent(
        """
        ██  ██ ██████      ██████ ██████
        ██  ██ ██      ██  ██  ██ ██  ██
        ██████ ██████      ██  ██ ██  ██
            ██     ██  ██  ██  ██ ██  ██
            ██ ██████      ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_17_minutes_and_four_seconds():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(1024, chars)) == (
        "  ██   ██████      ██████ ██  ██\n"
        " ███       ██  ██  ██  ██ ██  ██\n"
        "  ██      ██       ██  ██ ██████\n"
        "  ██     ██    ██  ██  ██     ██\n"
        "  ██     ██        ██████     ██"
    )


def test_get_number_lines_8_minutes_and_6_seconds():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(486, chars)) == dedent(
        """
        ██████  ████       ██████ ██████
        ██  ██ ██  ██  ██  ██  ██ ██
        ██  ██  ████       ██  ██ ██████
        ██  ██ ██  ██  ██  ██  ██ ██  ██
        ██████  ████       ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_9_minutes():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(540, chars)) == dedent(
        """
        ██████ ██████      ██████ ██████
        ██  ██ ██  ██  ██  ██  ██ ██  ██
        ██  ██ ██████      ██  ██ ██  ██
        ██  ██     ██  ██  ██  ██ ██  ██
        ██████  █████      ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_3478():
    # Use size 5 digits
    chars = CHARS_BY_SIZE[5]
    assert join_lines(timer.get_number_lines(2118, chars)) == dedent(
        """
        ██████ ██████        ██    ████
            ██ ██      ██   ███   ██  ██
         █████ ██████        ██    ████
            ██     ██  ██    ██   ██  ██
        ██████ ██████        ██    ████
    """
    ).strip("\n")
