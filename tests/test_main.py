"""Test cases for the __main__ module."""

import os
import re
from textwrap import dedent

import pytest
from click.testing import CliRunner

from countdown import __main__


class FakeSleep:
    """Fake time.sleep."""

    def __init__(self, *, raises={}):  # noqa: B006
        self.slept = 0
        self.raises = dict(raises)

    def __call__(self, seconds):
        self.slept += seconds
        if self.slept in self.raises:
            raise self.raises[self.slept]


def fake_size(
    columns,
    lines,
):
    def get_terminal_size(fallback=(columns, lines)):
        return os.terminal_size(fallback)

    return get_terminal_size


def clean_main_output(output):
    """Remove ANSI escape codes and whitespace at ends of lines."""
    output = re.sub(r"\033\[(\?\d+[hl]|[HJ])", "", output)
    output = re.sub(r" *\n", "\n", output)
    return output


def join_lines(lines):
    """Given list of lines, return string of lines with whitespace stripped."""
    return "\n".join(line.rstrip(" ") for line in lines)


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_invalid_duration():
    with pytest.raises(ValueError):
        __main__.duration("10")


def test_duration_10_seconds():
    assert __main__.duration("10s") == 10


def test_duration_60_seconds():
    assert __main__.duration("60s") == 60


def test_duration_1_minute():
    assert __main__.duration("1m") == 60


def test_duration_10_minutes():
    assert __main__.duration("10m") == 600


def test_duration_25_minutes():
    assert __main__.duration("25m") == 1500


def test_duration_3_minute_and_30_seconds():
    assert __main__.duration("3m30s") == 210


def test_duration_2_minutes_and_8_seconds():
    assert __main__.duration("2m8s") == 128


def test_get_number_lines_10_seconds(monkeypatch):
    # Use 40x6 terminal to select size 5 digits (33w <= 40, 5h <= 6)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(10)) == dedent(
        """
        ██████ ██████        ██   ██████
        ██  ██ ██  ██  ██   ███   ██  ██
        ██  ██ ██  ██        ██   ██  ██
        ██  ██ ██  ██  ██    ██   ██  ██
        ██████ ██████        ██   ██████
    """
    ).strip("\n")


def test_get_number_lines_60_seconds(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(60)) == dedent(
        """
        ██████   ██        ██████ ██████
        ██  ██  ███    ██  ██  ██ ██  ██
        ██  ██   ██        ██  ██ ██  ██
        ██  ██   ██    ██  ██  ██ ██  ██
        ██████   ██        ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_45_minutes(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(2700)) == dedent(
        """
        ██  ██ ██████      ██████ ██████
        ██  ██ ██      ██  ██  ██ ██  ██
        ██████ ██████      ██  ██ ██  ██
            ██     ██  ██  ██  ██ ██  ██
            ██ ██████      ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_17_minutes_and_four_seconds(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(1024)) == (
        "  ██   ██████      ██████ ██  ██\n"
        " ███       ██  ██  ██  ██ ██  ██\n"
        "  ██      ██       ██  ██ ██████\n"
        "  ██     ██    ██  ██  ██     ██\n"
        "  ██     ██        ██████     ██"
    )


def test_get_number_lines_8_minutes_and_6_seconds(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(486)) == dedent(
        """
        ██████  ████       ██████ ██████
        ██  ██ ██  ██  ██  ██  ██ ██
        ██  ██  ████       ██  ██ ██████
        ██  ██ ██  ██  ██  ██  ██ ██  ██
        ██████  ████       ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_9_minutes(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(540)) == dedent(
        """
        ██████ ██████      ██████ ██████
        ██  ██ ██  ██  ██  ██  ██ ██  ██
        ██  ██ ██████      ██  ██ ██  ██
        ██  ██     ██  ██  ██  ██ ██  ██
        ██████  █████      ██████ ██████
    """
    ).strip("\n")


def test_get_number_lines_3478(monkeypatch):
    # Use 40x6 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 6))
    assert join_lines(__main__.get_number_lines(2118)) == dedent(
        """
        ██████ ██████        ██    ████
            ██ ██      ██   ███   ██  ██
         █████ ██████        ██    ████
            ██     ██  ██    ██   ██  ██
        ██████ ██████        ██    ████
    """
    ).strip("\n")


def test_print_full_screen_tiny_terminal(
    capsys,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))
    __main__.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    assert out[6:] == "\n\n\n\n              hello world"


def test_print_full_screen_larger_terminal(
    capsys,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    __main__.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    # 24 height - 1 line = 23, 23//2 = 11 newlines
    # 80 width - 11 chars = 69, 69//2 = 34 spaces
    assert out[6:] == "\n" * 11 + " " * 34 + "hello world"


def test_print_full_screen_multiline_text(
    capsys,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(100, 30))
    __main__.print_full_screen(
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


def test_main_with_no_arguments(runner):
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.output == dedent(
        """\
        Usage: main [OPTIONS] DURATION
        Try 'main --help' for help.

        Error: Missing argument 'DURATION'.
    """
    )
    assert result.exit_code == 2


def test_version_works(runner):
    """It can print the version."""
    result = runner.invoke(__main__.main, ["--version"])
    assert ", version" in result.stdout
    assert result.exit_code == 0


def test_main_3_seconds_sleeps_4_times(
    runner,
    monkeypatch,
):
    # Use 40x20 terminal to select size 5 digits (33w <= 40, 5h <= 20)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 20))
    fake_sleep = FakeSleep()
    monkeypatch.setattr("time.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["3s"])
    assert result.exit_code == 0
    assert clean_main_output(result.stdout) == (
        "\n\n\n\n\n\n\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██  ██     ██\n"
        "   ██  ██ ██  ██      ██  ██  █████\n"
        "   ██  ██ ██  ██  ██  ██  ██     ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n\n\n\n\n\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██  ██     ██\n"
        "   ██  ██ ██  ██      ██  ██ ██████\n"
        "   ██  ██ ██  ██  ██  ██  ██ ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n\n\n\n\n\n"
        "   ██████ ██████      ██████   ██\n"
        "   ██  ██ ██  ██  ██  ██  ██  ███\n"
        "   ██  ██ ██  ██      ██  ██   ██\n"
        "   ██  ██ ██  ██  ██  ██  ██   ██\n"
        "   ██████ ██████      ██████   ██\n"
        "\n\n\n\n\n\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██  ██ ██  ██\n"
        "   ██  ██ ██  ██      ██  ██ ██  ██\n"
        "   ██  ██ ██  ██  ██  ██  ██ ██  ██\n"
        "   ██████ ██████      ██████ ██████ "
    )
    assert fake_sleep.slept == 4  # 3 seconds = 4 sleeps


def test_main_1_minute(
    runner,
    monkeypatch,
):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h <= 10)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))

    # Raise exception after 11 sleeps
    fake_sleep = FakeSleep(raises={11: SystemExit(0)})
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["1m"])
    assert clean_main_output(result.stdout) == (
        "\n\n"
        "   ██████   ██        ██████ ██████\n"
        "   ██  ██  ███    ██  ██  ██ ██  ██\n"
        "   ██  ██   ██        ██  ██ ██  ██\n"
        "   ██  ██   ██    ██  ██  ██ ██  ██\n"
        "   ██████   ██        ██████ ██████\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██     ██  ██\n"
        "   ██  ██ ██  ██      ██████ ██████\n"
        "   ██  ██ ██  ██  ██      ██     ██\n"
        "   ██████ ██████      ██████  █████\n"
        "\n"
        "   ██████ ██████      ██████  ████\n"
        "   ██  ██ ██  ██  ██  ██     ██  ██\n"
        "   ██  ██ ██  ██      ██████  ████\n"
        "   ██  ██ ██  ██  ██      ██ ██  ██\n"
        "   ██████ ██████      ██████  ████\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██         ██\n"
        "   ██  ██ ██  ██      ██████    ██\n"
        "   ██  ██ ██  ██  ██      ██   ██\n"
        "   ██████ ██████      ██████   ██\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██     ██\n"
        "   ██  ██ ██  ██      ██████ ██████\n"
        "   ██  ██ ██  ██  ██      ██ ██  ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██     ██\n"
        "   ██  ██ ██  ██      ██████ ██████\n"
        "   ██  ██ ██  ██  ██      ██     ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n"
        "   ██████ ██████      ██████ ██  ██\n"
        "   ██  ██ ██  ██  ██  ██     ██  ██\n"
        "   ██  ██ ██  ██      ██████ ██████\n"
        "   ██  ██ ██  ██  ██      ██     ██\n"
        "   ██████ ██████      ██████     ██\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██         ██\n"
        "   ██  ██ ██  ██      ██████  █████\n"
        "   ██  ██ ██  ██  ██      ██     ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██         ██\n"
        "   ██  ██ ██  ██      ██████ ██████\n"
        "   ██  ██ ██  ██  ██      ██ ██\n"
        "   ██████ ██████      ██████ ██████\n"
        "\n"
        "   ██████ ██████      ██████   ██\n"
        "   ██  ██ ██  ██  ██  ██      ███\n"
        "   ██  ██ ██  ██      ██████   ██\n"
        "   ██  ██ ██  ██  ██      ██   ██\n"
        "   ██████ ██████      ██████   ██\n"
        "\n"
        "   ██████ ██████      ██████ ██████\n"
        "   ██  ██ ██  ██  ██  ██     ██  ██\n"
        "   ██  ██ ██  ██      ██████ ██  ██\n"
        "   ██  ██ ██  ██  ██      ██ ██  ██\n"
        "   ██████ ██████      ██████ ██████ "
    )


def test_main_10_minutes_has_over_600_clear_screens(
    runner,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    fake_sleep = FakeSleep()
    monkeypatch.setattr("time.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["10m"])
    assert fake_sleep.slept == 601  # 10 minutes = 601 sleeps
    assert result.stdout.count("\033[H\033[J") == 601


def test_main_enables_alt_buffer_and_hides_cursor_at_beginning(
    runner,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    fake_sleep = FakeSleep()
    monkeypatch.setattr("time.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.startswith("\033[?1049h\033[?25l")


def test_main_disable_alt_buffer_and_show_cursor_at_end(
    runner,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    fake_sleep = FakeSleep()
    monkeypatch.setattr("time.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_main_early_exit_still_shows_cursor_at_end(
    runner,
    monkeypatch,
):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h <= 10)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))

    # Hit Ctrl+C after 4 seconds
    fake_sleep = FakeSleep(raises={4: KeyboardInterrupt()})
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["15m"])
    assert len(result.stdout.splitlines()) == 25, "4 seconds of lines printed"
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_digit_sizes_available():
    """Test that expected digit sizes are available."""
    from countdown.digits import DIGIT_SIZES

    assert 16 in DIGIT_SIZES, "Size 16 digits should be available"
    assert 7 in DIGIT_SIZES, "Size 7 digits should be available"
    assert 5 in DIGIT_SIZES, "Size 5 digits should be available"
    assert 3 in DIGIT_SIZES, "Size 3 digits should be available"
    assert 1 in DIGIT_SIZES, "Size 1 digits should be available"


def test_all_characters_in_each_size():
    """Test that all digit characters exist in each size."""
    from countdown.digits import CHARS_BY_SIZE, DIGIT_SIZES

    expected_chars = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", ":"}
    for size in DIGIT_SIZES:
        chars = CHARS_BY_SIZE[size]
        assert set(chars.keys()) == expected_chars, (
            f"Size {size} should have all characters"
        )


def test_char_heights_match_size():
    """Test that character heights match the expected size."""
    from countdown.digits import CHARS_BY_SIZE, DIGIT_SIZES

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
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 7, "80x24 terminal should select size 7"

    # 100x24 terminal - size 16 fits (93w <= 100, 16h <= 24)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(100, 24))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 16, "100x24 terminal should select size 16"

    # 60x20 terminal - size 7 fits (57w <= 60, 7h <= 20)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(60, 20))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 7, "60x20 terminal should select size 7"

    # 32x10 terminal - size 3 fits (20w <= 32, 3h <= 10)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 3, "32x10 terminal should select size 3"

    # 15x5 terminal - size 1 fits (10w <= 15, 1h <= 5)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(15, 5))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, "15x5 terminal should select size 1"

    # Very small terminal - falls back to smallest
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(5, 1))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, "5x1 terminal should fall back to size 1"


def test_different_sizes_render_correctly(monkeypatch):
    """Test that different sizes render correctly."""
    # Test size 7 rendering (80x24 selects size 7)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    lines = __main__.get_number_lines(0)  # 00:00
    assert len(lines) == 7, "80x24 terminal should render 7 lines"

    # Test size 3 rendering (32x10 selects size 3)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    lines = __main__.get_number_lines(0)  # 00:00
    assert len(lines) == 3, "32x10 terminal should render 3 lines"

    # Test size 1 rendering (15x5 selects size 1)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(15, 5))
    lines = __main__.get_number_lines(0)  # 00:00
    assert len(lines) == 1, "15x5 terminal should render 1 line"


def test_width_constraints_force_smaller_size(monkeypatch):
    """Test that narrow terminal widths force selection of smaller digit sizes."""
    # Size 7 requires 57 width - a 56x20 terminal should select size 5 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(56, 20))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 5, (
        "56x20 terminal too narrow for size 7, should select size 5"
    )

    # Size 5 requires 33 width - a 32x10 terminal should select size 3 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 3, (
        "32x10 terminal too narrow for size 5, should select size 3"
    )

    # Size 3 requires 20 width - a 19x5 terminal should select size 1 instead
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(19, 5))
    chars = __main__.get_chars_for_terminal()
    height = len(chars["0"].splitlines())
    assert height == 1, (
        "19x5 terminal too narrow for size 3, should select size 1"
    )
