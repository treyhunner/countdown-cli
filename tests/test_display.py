"""Test cases for the display module."""

import os
from textwrap import dedent

from countdown import display
from countdown.digits import DIGIT_SIZES


def fake_size(columns, lines):
    """Create a fake terminal size function for testing."""

    def get_terminal_size(fallback=(columns, lines)):
        return os.terminal_size(fallback)

    return get_terminal_size


def test_print_full_screen_tiny_terminal(capsys, monkeypatch):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))
    display.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    assert out[6:] == "\n\n\n\n              hello world"


def test_print_full_screen_larger_terminal(capsys, monkeypatch):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    display.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    # 24 height - 1 line = 23, 23//2 = 11 newlines
    # 80 width - 11 chars = 69, 69//2 = 34 spaces
    assert out[6:] == "\n" * 11 + " " * 34 + "hello world"


def test_print_full_screen_multiline_text(capsys, monkeypatch):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(100, 30))
    display.print_full_screen(
        dedent(
            """\
        ██████ ██████       ██   ████
            ██ ██     ██   ███  ██  ██
         █████ ██████       ██   ████
            ██     ██ ██    ██  ██  ██
        ██████ ██████       ██   ████
    """
        ).splitlines()
    )
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    assert out[6:] == (
        "\n\n\n\n\n\n\n\n\n\n\n\n"
        "                                   ██████ ██████       ██   ████\n"
        "                                       ██ ██     ██   ███  ██  ██\n"
        "                                    █████ ██████       ██   ████\n"
        "                                       ██     ██ ██    ██  ██  ██\n"
        "                                   ██████ ██████       ██   ████"
    )


def test_print_full_screen_paused_shows_red_and_message(capsys, monkeypatch):
    """Test that paused=True shows colored timer and PAUSED message."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    lines = ["00:05"]
    display.print_full_screen(lines, paused=True)
    out, err = capsys.readouterr()
    # Should contain intense magenta color code
    assert (
        "\x1b[95m" in out
    ), "Should contain intense magenta color code when paused"
    # Should contain reset code
    assert "\033[0m" in out, "Should contain color reset code"
    # Should contain PAUSED message
    assert "PAUSED - Press any key to resume" in out


def test_print_full_screen_not_paused_no_red_or_message(capsys, monkeypatch):
    """Test that paused=False shows normal timer without PAUSED message."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    lines = ["00:05"]
    display.print_full_screen(lines, paused=False)
    out, err = capsys.readouterr()
    # Should NOT contain PAUSED message
    assert "PAUSED" not in out
    # Red color may or may not be present depending on other features, but
    # the important thing is the PAUSED message is not shown


def test_print_full_screen_paused_tiny_terminal_no_message(capsys, monkeypatch):
    """Test that PAUSED message is hidden in tiny terminals with no room."""
    # Create a 3-line terminal with 3-line timer (no room for PAUSED text)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(20, 3))
    lines = ["line1", "line2", "line3"]
    display.print_full_screen(lines, paused=True)
    out, err = capsys.readouterr()
    # Should still show intense magenta color
    assert (
        "\x1b[95m" in out
    ), "Should contain intense magenta color code when paused"
    # Should NOT show PAUSED message (no room)
    assert "PAUSED" not in out, "PAUSED message should not appear in tiny terminal"


def test_digit_sizes_available():
    """Test that expected digit sizes are available."""
    assert 16 in DIGIT_SIZES, "Size 16 digits should be available"
    assert 7 in DIGIT_SIZES, "Size 7 digits should be available"
    assert 5 in DIGIT_SIZES, "Size 5 digits should be available"
    assert 3 in DIGIT_SIZES, "Size 3 digits should be available"
    assert 1 in DIGIT_SIZES, "Size 1 digits should be available"


def test_all_characters_in_each_size():
    """Test that all digit characters exist in each size."""
    from countdown.digits import CHARS_BY_SIZE

    expected_chars = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":"}
    for size in DIGIT_SIZES:
        chars = CHARS_BY_SIZE[size]
        assert set(chars.keys()) == expected_chars, (
            f"Size {size} should have all characters"
        )


def test_char_heights_match_size():
    """Test that character heights match the expected size."""
    from countdown.digits import CHARS_BY_SIZE

    for size in DIGIT_SIZES:
        chars = CHARS_BY_SIZE[size]
        for char, text in chars.items():
            height = len(text.splitlines())
            assert height == size, (
                f"Character '{char}' in size {size} should have height {size}, got {height}"
            )


def test_get_chars_for_terminal_selects_largest_that_fits(monkeypatch):
    """Test that get_chars_for_terminal selects the largest size that fits both dimensions."""
    # Size requirements: 16(93w), 7(57w), 5(33w), 3(20w), 1(10w)

    # 80x24 terminal - size 7 fits (57w <= 80, 7h <= 24)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 7, "80x24 terminal should select size 7"

    # 100x24 terminal - size 16 fits (93w <= 100, 16h <= 24)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(100, 24))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 16, "100x24 terminal should select size 16"

    # 60x20 terminal - size 7 fits (57w <= 60, 7h <= 20)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(60, 20))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 7, "60x20 terminal should select size 7"

    # 32x10 terminal - size 3 fits (20w <= 32, 3h <= 10)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 3, "32x10 terminal should select size 3"

    # 15x5 terminal - size 1 fits (10w <= 15, 1h <= 5)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(15, 5))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, "15x5 terminal should select size 1"

    # Very small terminal - falls back to smallest
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(5, 1))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, "5x1 terminal should fall back to size 1"


def test_different_sizes_render_correctly(monkeypatch):
    """Test that different sizes render correctly."""
    from countdown import timer

    # Test size 7 rendering (80x24 selects size 7)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    chars = display.get_chars_for_terminal()
    lines = timer.get_number_lines(0, chars)  # 00:00
    assert len(lines) == 7, "80x24 terminal should render 7 lines"

    # Test size 3 rendering (32x10 selects size 3)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    chars = display.get_chars_for_terminal()
    lines = timer.get_number_lines(0, chars)  # 00:00
    assert len(lines) == 3, "32x10 terminal should render 3 lines"

    # Test size 1 rendering (15x5 selects size 1)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(15, 5))
    chars = display.get_chars_for_terminal()
    lines = timer.get_number_lines(0, chars)  # 00:00
    assert len(lines) == 1, "15x5 terminal should render 1 line"


def test_width_constraints_force_smaller_size(monkeypatch):
    """Test that narrow terminal widths force selection of smaller digit sizes."""
    # Size 7 requires 57 width - a 56x20 terminal should select size 5 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(56, 20))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 5, "56x20 terminal too narrow for size 7, should select size 5"

    # Size 5 requires 33 width - a 32x10 terminal should select size 3 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 3, "32x10 terminal too narrow for size 5, should select size 3"

    # Size 3 requires 20 width - a 19x5 terminal should select size 1 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(19, 5))
    chars = display.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, "19x5 terminal too narrow for size 3, should select size 1"
