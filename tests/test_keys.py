"""Test cases for the keys module."""

from countdown import keys


def test_is_pause_key_with_strings():
    """Test that is_pause_key recognizes pause keys as strings (Unix)."""
    assert keys.is_pause_key(" ") is True, "Space should be a pause key"
    assert keys.is_pause_key("p") is True, "p should be a pause key"
    assert keys.is_pause_key("k") is True, "k should be a pause key"
    assert keys.is_pause_key("\r") is True, "Carriage return should be a pause key"
    assert keys.is_pause_key("\n") is True, "Newline should be a pause key"
    assert keys.is_pause_key("a") is False, "a should not be a pause key"
    assert keys.is_pause_key("x") is False, "x should not be a pause key"
    assert keys.is_pause_key("q") is False, "q should not be a pause key"


def test_is_time_adjust_key_with_strings():
    """Test that is_time_adjust_key recognizes +, =, - as strings (Unix)."""
    assert keys.is_time_adjust_key("+") is True, "+ should be a time adjust key"
    assert keys.is_time_adjust_key("=") is True, "= should be a time adjust key"
    assert keys.is_time_adjust_key("-") is True, "- should be a time adjust key"
    assert keys.is_time_adjust_key("a") is False, "a should not be a time adjust key"
    assert (
        keys.is_time_adjust_key(" ") is False
    ), "space should not be a time adjust key"


def test_get_time_adjustment():
    """Test that get_time_adjustment returns correct values."""
    assert keys.get_time_adjustment("+") == 30, "+ should add 30 seconds"
    assert keys.get_time_adjustment("=") == 30, "= should add 30 seconds"
    assert keys.get_time_adjustment("-") == -30, "- should subtract 30 seconds"
    assert keys.get_time_adjustment("a") == 0, "non-adjust key should return 0"
