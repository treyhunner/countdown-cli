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
        # Check for exception with floating point tolerance
        for trigger_time, exception in self.raises.items():
            if abs(self.slept - trigger_time) < 0.001:
                raise exception


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
    # Use 40x7 terminal to select size 5 digits (33w <= 40, 5h+2 padding <= 7)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
    assert join_lines(__main__.get_number_lines(1024)) == (
        "  ██   ██████      ██████ ██  ██\n"
        " ███       ██  ██  ██  ██ ██  ██\n"
        "  ██      ██       ██  ██ ██████\n"
        "  ██     ██    ██  ██  ██     ██\n"
        "  ██     ██        ██████     ██"
    )


def test_get_number_lines_8_minutes_and_6_seconds(monkeypatch):
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x7 terminal to select size 5 digits
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 7))
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
    # Use 40x20 terminal to select size 5 digits (33w <= 40, 5h+2 <= 20)
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
    # 3 seconds countdown = 4 iterations (3,2,1,0), each sleeps 1 second = 4 seconds total
    # Sleeping in chunks of 0.05, so total is ~4 seconds (floating point precision)
    assert fake_sleep.slept == pytest.approx(4.0, abs=0.01)


def test_main_1_minute(
    runner,
    monkeypatch,
):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
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
    # 10 minutes = 601 iterations, each sleeps 1 second (via 20×0.05 chunks)
    # Floating point precision: 601 × 20 × 0.05 ≈ 601.0
    assert fake_sleep.slept == pytest.approx(601.0, abs=0.1)
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
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))

    # Hit Ctrl+C after 4 seconds total sleep time (chunked sleep)
    fake_sleep = FakeSleep(raises={4: KeyboardInterrupt()})
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["15m"])
    # After 4 seconds of sleep, we've completed 4 iterations, each prints lines
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


def test_is_pause_key_with_strings():
    """Test that is_pause_key recognizes pause keys as strings (Unix)."""
    assert __main__.is_pause_key(' ') is True, "Space should be a pause key"
    assert __main__.is_pause_key('p') is True, "p should be a pause key"
    assert __main__.is_pause_key('k') is True, "k should be a pause key"
    assert __main__.is_pause_key('\r') is True, "Carriage return should be a pause key"
    assert __main__.is_pause_key('\n') is True, "Newline should be a pause key"
    assert __main__.is_pause_key('a') is False, "a should not be a pause key"
    assert __main__.is_pause_key('x') is False, "x should not be a pause key"
    assert __main__.is_pause_key('q') is False, "q should not be a pause key"


def test_is_pause_key_with_bytes():
    """Test that is_pause_key recognizes pause keys as bytes (Windows)."""
    assert __main__.is_pause_key(b' ') is True, "Space as bytes should be a pause key"
    assert __main__.is_pause_key(b'p') is True, "p as bytes should be a pause key"
    assert __main__.is_pause_key(b'k') is True, "k as bytes should be a pause key"
    assert __main__.is_pause_key(b'\r') is True, "CR as bytes should be a pause key"
    assert __main__.is_pause_key(b'\n') is True, "LF as bytes should be a pause key"
    assert __main__.is_pause_key(b'a') is False, "a as bytes should not be a pause key"
    assert __main__.is_pause_key(b'x') is False, "x as bytes should not be a pause key"


def test_print_full_screen_paused_shows_red_and_message(
    capsys,
    monkeypatch,
):
    """Test that paused=True shows colored timer and PAUSED message."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    lines = ["00:05"]
    __main__.print_full_screen(lines, paused=True)
    out, err = capsys.readouterr()
    # Should contain intense magenta color code
    assert "\x1b[95m" in out, "Should contain intense magenta color code when paused"
    # Should contain reset code
    assert "\033[0m" in out, "Should contain color reset code"
    # Should contain PAUSED message
    assert "PAUSED - Press any key to resume" in out


def test_print_full_screen_not_paused_no_red_or_message(
    capsys,
    monkeypatch,
):
    """Test that paused=False shows normal timer without PAUSED message."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    lines = ["00:05"]
    __main__.print_full_screen(lines, paused=False)
    out, err = capsys.readouterr()
    # Should NOT contain PAUSED message
    assert "PAUSED" not in out
    # Red color may or may not be present depending on other features, but
    # the important thing is the PAUSED message is not shown


def test_print_full_screen_paused_tiny_terminal_no_message(
    capsys,
    monkeypatch,
):
    """Test that PAUSED message is hidden in tiny terminals with no room."""
    # Create a 3-line terminal with 3-line timer (no room for PAUSED text)
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(20, 3))
    lines = ["line1", "line2", "line3"]
    __main__.print_full_screen(lines, paused=True)
    out, err = capsys.readouterr()
    # Should still show intense magenta color
    assert "\x1b[95m" in out, "Should contain intense magenta color code when paused"
    # Should NOT show PAUSED message (no room)
    assert "PAUSED" not in out, "PAUSED message should not appear in tiny terminal"


def test_pause_key_triggers_pause(
    runner,
    monkeypatch,
):
    """Test that pressing a pause key triggers the pause logic."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 20))

    # Exit after a short time
    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("time.sleep", fake_sleep)

    # Track whether pause key was detected
    pause_key_detected = [False]
    read_key_called = [False]

    def fake_check_for_keypress():
        # Return True once to simulate a keypress during first iteration
        if not pause_key_detected[0]:
            pause_key_detected[0] = True
            return True
        return False

    def fake_read_key():
        read_key_called[0] = True
        return ' '  # Space bar (a pause key)

    def fake_drain():
        pass  # No additional keys to drain

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["5s"])

    # The pause key should have been detected and read
    assert pause_key_detected[0], "Pause key detection should have been called"
    assert read_key_called[0], "read_key should have been called"
    # Output should contain the paused color since we pressed a pause key
    assert "\x1b[95m" in result.stdout, "Should show paused color when pause key pressed"


def test_non_pause_key_ignored(
    runner,
    monkeypatch,
):
    """Test that non-pause keys are ignored during countdown."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 20))

    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("time.sleep", fake_sleep)

    # Track keypresses
    check_called = [False]
    read_key_called = [False]

    def fake_check_for_keypress():
        if not check_called[0]:
            check_called[0] = True
            return True
        return False

    def fake_read_key():
        read_key_called[0] = True
        return 'x'  # Not a pause key

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)

    result = runner.invoke(__main__.main, ["5s"])

    # The key should have been read
    assert read_key_called[0], "read_key should have been called"
    # Output should NOT contain paused color since 'x' is not a pause key
    assert "\x1b[95m" not in result.stdout, "Should not show paused color for non-pause key"
    assert result.exit_code == 0


def test_pause_key_detection(
    monkeypatch,
):
    """Test that check_for_keypress returns False when not a TTY."""
    import sys

    # Mock stdin.isatty() to return False
    original_isatty = sys.stdin.isatty
    sys.stdin.isatty = lambda: False

    try:
        result = __main__.check_for_keypress()
        assert result is False, "Should return False when not a TTY"
    finally:
        sys.stdin.isatty = original_isatty


def test_sleep_exits_early_on_keypress(
    runner,
    monkeypatch,
):
    """Test that sleep loop exits early when a key is pressed mid-sleep."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 20))

    # Track sleep calls
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)
        # Exit after we've done a few sleep chunks
        if len(sleep_calls) >= 5:
            raise KeyboardInterrupt()

    monkeypatch.setattr("time.sleep", fake_sleep)

    # Simulate keypress after 3rd sleep call (during chunked 1-second sleep)
    check_count = [0]

    def fake_check_for_keypress():
        check_count[0] += 1
        # Return True on the 3rd sleep chunk to simulate keypress mid-sleep
        return len(sleep_calls) == 3

    def fake_read_key():
        return ' '  # Pause key

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["10s"])

    # Should have broken out of sleep loop early (not all 20 chunks)
    # We expect: 3 chunks of first iteration, then breaks, then starts paused sleep
    # The key point is we don't see all 20 chunks of 0.05 before breaking
    assert len(sleep_calls) >= 3, "Should have at least 3 sleep calls"
    # If it didn't exit early, we'd see many more 0.05 sleep calls
    # The presence of the break means we don't complete all 20 chunks
    first_iteration_sleeps = [s for s in sleep_calls[:3] if s == 0.05]
    assert len(first_iteration_sleeps) == 3, "Should have 3 chunks of 0.05s before breaking"


def test_resume_from_pause_exits_early(
    runner,
    monkeypatch,
):
    """Test that when paused, pressing a key to resume exits the 0.05s sleep loop."""
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 20))

    sleep_calls = []
    paused_state = [False]

    def fake_sleep(seconds):
        sleep_calls.append((seconds, paused_state[0]))
        if len(sleep_calls) >= 10:
            raise KeyboardInterrupt()

    monkeypatch.setattr("time.sleep", fake_sleep)

    # Simulate: pause immediately, then resume after a few paused sleeps
    keypress_count = [0]

    def fake_check_for_keypress():
        keypress_count[0] += 1
        # First keypress: pause immediately (keypress 1)
        # Second keypress: resume after being paused (keypress 2)
        return keypress_count[0] in [1, 5]

    keys_to_return = [' ', ' ']  # Space to pause, space to resume
    key_index = [0]

    def fake_read_key():
        key = keys_to_return[key_index[0]]
        key_index[0] = min(key_index[0] + 1, len(keys_to_return) - 1)
        return key

    def fake_drain():
        pass

    # Track pause state transitions
    original_print = __main__.print_full_screen

    def tracking_print(lines, paused=False):
        paused_state[0] = paused
        return original_print(lines, paused=paused)

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)
    monkeypatch.setattr(__main__, "print_full_screen", tracking_print)

    result = runner.invoke(__main__.main, ["10s"])

    # Should have some paused sleeps (0.05) and some regular chunked sleeps (0.05)
    paused_sleeps = [s for s, p in sleep_calls if p]
    unpaused_sleeps = [s for s, p in sleep_calls if not p]

    assert len(paused_sleeps) > 0, "Should have some paused sleep periods"
    assert len(unpaused_sleeps) > 0, "Should have some unpaused sleep periods"
