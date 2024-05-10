"""Test cases for the __main__ module."""

import os
import re
from textwrap import dedent
from textwrap import indent

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


def test_get_number_lines_10_seconds():
    assert (
        join_lines(__main__.get_number_lines(10))
        == dedent(
            """
        ██████ ██████       ██  ██████
        ██  ██ ██  ██ ██   ███  ██  ██
        ██  ██ ██  ██       ██  ██  ██
        ██  ██ ██  ██ ██    ██  ██  ██
        ██████ ██████       ██  ██████
    """
        ).strip("\n")
    )


def test_get_number_lines_60_seconds():
    assert (
        join_lines(__main__.get_number_lines(60))
        == dedent(
            """
        ██████    ██     ██████ ██████
        ██  ██   ███  ██ ██  ██ ██  ██
        ██  ██    ██     ██  ██ ██  ██
        ██  ██    ██  ██ ██  ██ ██  ██
        ██████    ██     ██████ ██████
    """
        ).strip("\n")
    )


def test_get_number_lines_45_minutes():
    assert (
        join_lines(__main__.get_number_lines(2700))
        == dedent(
            """
        ██  ██ ██████    ██████ ██████
        ██  ██ ██     ██ ██  ██ ██  ██
        ██████ ██████    ██  ██ ██  ██
            ██     ██ ██ ██  ██ ██  ██
            ██ ██████    ██████ ██████
    """
        ).strip("\n")
    )


def test_get_number_lines_17_minutes_and_four_seconds():
    assert join_lines(__main__.get_number_lines(1024)) == indent(
        dedent(
            """
         ██  ██████    ██████ ██  ██
        ███      ██ ██ ██  ██ ██  ██
         ██     ██     ██  ██ ██████
         ██    ██   ██ ██  ██     ██
         ██    ██      ██████     ██
    """
        ).strip("\n"),
        "  ",
    )


def test_get_number_lines_8_minutes_and_6_seconds():
    assert (
        join_lines(__main__.get_number_lines(486))
        == dedent(
            """
        ██████  ████     ██████ ██████
        ██  ██ ██  ██ ██ ██  ██ ██
        ██  ██  ████     ██  ██ ██████
        ██  ██ ██  ██ ██ ██  ██ ██  ██
        ██████  ████     ██████ ██████
    """
        ).strip("\n")
    )


def test_get_number_lines_9_minutes():
    assert (
        join_lines(__main__.get_number_lines(540))
        == dedent(
            """
        ██████ ██████    ██████ ██████
        ██  ██ ██  ██ ██ ██  ██ ██  ██
        ██  ██ ██████    ██  ██ ██  ██
        ██  ██     ██ ██ ██  ██ ██  ██
        ██████  █████    ██████ ██████
    """
        ).strip("\n")
    )


def test_get_number_lines_3478():
    assert (
        join_lines(__main__.get_number_lines(2118))
        == dedent(
            """
        ██████ ██████       ██   ████
            ██ ██     ██   ███  ██  ██
         █████ ██████       ██   ████
            ██     ██ ██    ██  ██  ██
        ██████ ██████       ██   ████
    """
        ).strip("\n")
    )


def fake_size(
    columns,
    lines,
):
    def get_terminal_size(fallback=(columns, lines)):
        return os.terminal_size(fallback)

    return get_terminal_size


def test_print_full_screen_tiny_terminal(
    capsys,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(40, 10))
    __main__.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    assert (
        out[6:]
        == """


              hello world
    """.rstrip(
            " "
        )
    )


def test_print_full_screen_larger_terminal(
    capsys,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(80, 24))
    __main__.print_full_screen(["hello world"])
    out, err = capsys.readouterr()
    assert out[:6] == "\x1b[H\x1b[J"
    assert (
        out[6:]
        == """









                                  hello world
        """.rstrip(
            " "
        )
    )


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
    assert (
        out[6:]
        == """










                                   ██████ ██████       ██   ████
                                       ██ ██     ██   ███  ██  ██
                                    █████ ██████       ██   ████
                                       ██     ██ ██    ██  ██  ██
                                   ██████ ██████       ██   ████
    """.rstrip(
            " "
        )
    )


def test_main_with_no_arguments(runner):
    """It exits with a status code of zero."""
    result = runner.invoke(__main__.main)
    assert result.stdout == dedent(
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
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(60, 20))
    fake_sleep = FakeSleep()
    monkeypatch.setattr("time.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["3s"])
    assert result.exit_code == 0
    assert (
        clean_main_output(result.stdout)
        == """





              ██████ ██████    ██████ ██████
              ██  ██ ██  ██ ██ ██  ██     ██
              ██  ██ ██  ██    ██  ██  █████
              ██  ██ ██  ██ ██ ██  ██     ██
              ██████ ██████    ██████ ██████






              ██████ ██████    ██████ ██████
              ██  ██ ██  ██ ██ ██  ██     ██
              ██  ██ ██  ██    ██  ██ ██████
              ██  ██ ██  ██ ██ ██  ██ ██
              ██████ ██████    ██████ ██████






              ██████ ██████    ██████    ██
              ██  ██ ██  ██ ██ ██  ██   ███
              ██  ██ ██  ██    ██  ██    ██
              ██  ██ ██  ██ ██ ██  ██    ██
              ██████ ██████    ██████    ██






              ██████ ██████    ██████ ██████
              ██  ██ ██  ██ ██ ██  ██ ██  ██
              ██  ██ ██  ██    ██  ██ ██  ██
              ██  ██ ██  ██ ██ ██  ██ ██  ██
              ██████ ██████    ██████ ██████
    """.rstrip(
            " "
        )
    )
    assert fake_sleep.slept == 4  # 3 seconds = 4 sleeps


def test_main_1_minute(
    runner,
    monkeypatch,
):
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))

    # Raise exception after 11 sleeps
    fake_sleep = FakeSleep(raises={11: SystemExit(0)})
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["1m"])
    assert (
        clean_main_output(result.stdout)
        == """
██████    ██     ██████ ██████
██  ██   ███  ██ ██  ██ ██  ██
██  ██    ██     ██  ██ ██  ██
██  ██    ██  ██ ██  ██ ██  ██
██████    ██     ██████ ██████

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██     ██  ██
██  ██ ██  ██    ██████ ██████
██  ██ ██  ██ ██     ██     ██
██████ ██████    ██████  █████

██████ ██████    ██████  ████
██  ██ ██  ██ ██ ██     ██  ██
██  ██ ██  ██    ██████  ████
██  ██ ██  ██ ██     ██ ██  ██
██████ ██████    ██████  ████

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██         ██
██  ██ ██  ██    ██████    ██
██  ██ ██  ██ ██     ██   ██
██████ ██████    ██████   ██

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██     ██
██  ██ ██  ██    ██████ ██████
██  ██ ██  ██ ██     ██ ██  ██
██████ ██████    ██████ ██████

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██     ██
██  ██ ██  ██    ██████ ██████
██  ██ ██  ██ ██     ██     ██
██████ ██████    ██████ ██████

██████ ██████    ██████ ██  ██
██  ██ ██  ██ ██ ██     ██  ██
██  ██ ██  ██    ██████ ██████
██  ██ ██  ██ ██     ██     ██
██████ ██████    ██████     ██

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██         ██
██  ██ ██  ██    ██████  █████
██  ██ ██  ██ ██     ██     ██
██████ ██████    ██████ ██████

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██         ██
██  ██ ██  ██    ██████ ██████
██  ██ ██  ██ ██     ██ ██
██████ ██████    ██████ ██████

██████ ██████    ██████    ██
██  ██ ██  ██ ██ ██       ███
██  ██ ██  ██    ██████    ██
██  ██ ██  ██ ██     ██    ██
██████ ██████    ██████    ██

██████ ██████    ██████ ██████
██  ██ ██  ██ ██ ██     ██  ██
██  ██ ██  ██    ██████ ██  ██
██  ██ ██  ██ ██     ██ ██  ██
██████ ██████    ██████ ██████
                """.rstrip(
            " "
        )
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
    monkeypatch.setattr("shutil.get_terminal_size", fake_size(32, 10))

    # Hit Ctrl+C after 4 seconds
    fake_sleep = FakeSleep(raises={4: KeyboardInterrupt()})
    monkeypatch.setattr("time.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["15m"])
    assert len(result.stdout.splitlines()) == 25, "4 seconds of lines printed"
    assert result.stdout.endswith("\033[?25h\033[?1049l")
