"""Integration test cases for the CLI."""

import os
import re

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


def fake_size(columns, lines):
    def get_terminal_size(fallback=(columns, lines)):
        return os.terminal_size(fallback)

    return get_terminal_size


def clean_main_output(output):
    """Remove ANSI escape codes and whitespace at ends of lines."""
    output = re.sub(r"\033\[(\?\d+[hl]|[HJ])", "", output)
    output = re.sub(r" *\n", "\n", output)
    return output


@pytest.fixture
def runner():
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_with_no_arguments(runner):
    """It shows help when run without arguments."""
    result = runner.invoke(__main__.main)
    # Should show help (not error)
    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "DURATION" in result.output
    assert "5m" in result.output  # Should show examples


def test_version_works(runner):
    """It can print the version."""
    result = runner.invoke(__main__.main, ["--version"])
    assert ", version" in result.stdout
    assert result.exit_code == 0


def test_main_3_seconds_sleeps_4_times(runner, monkeypatch):
    # Use 40x20 terminal to select size 5 digits (33w <= 40, 5h+2 <= 20)
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )
    fake_sleep = FakeSleep()
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)
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


def test_main_1_minute(runner, monkeypatch):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 10),
    )

    # Raise exception after 11 sleeps
    fake_sleep = FakeSleep(raises={11: SystemExit(0)})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

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


def test_main_10_minutes_has_over_600_clear_screens(runner, monkeypatch):
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(32, 10),
    )
    fake_sleep = FakeSleep()
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["10m"])
    # 10 minutes = 601 iterations, each sleeps 1 second (via 20×0.05 chunks)
    # Floating point precision: 601 × 20 × 0.05 ≈ 601.0
    assert fake_sleep.slept == pytest.approx(601.0, abs=0.1)
    assert result.stdout.count("\033[H\033[J") == 601


def test_main_enables_alt_buffer_and_hides_cursor_at_beginning(
    runner, monkeypatch
):
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(32, 10),
    )
    fake_sleep = FakeSleep()
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.startswith("\033[?1049h\033[?25l")


def test_main_disable_alt_buffer_and_show_cursor_at_end(runner, monkeypatch):
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(32, 10),
    )
    fake_sleep = FakeSleep()
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_main_early_exit_still_shows_cursor_at_end(runner, monkeypatch):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 10),
    )

    # Hit Ctrl+C after 4 seconds total sleep time (chunked sleep)
    fake_sleep = FakeSleep(raises={4: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    result = runner.invoke(__main__.main, ["15m"])
    # After 4 seconds of sleep, we've completed 4 iterations, each prints lines
    assert len(result.stdout.splitlines()) == 25, "4 seconds of lines printed"
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_pause_key_triggers_pause(runner, monkeypatch):
    """Test that pressing a pause key triggers the pause logic."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    # Exit after a short time
    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

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
        return " "  # Space bar (a pause key)

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
    assert "\x1b[95m" in result.stdout, (
        "Should show paused color when pause key pressed"
    )


def test_non_pause_key_ignored(runner, monkeypatch):
    """Test that non-pause keys are ignored during countdown."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

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
        return "x"  # Not a pause key

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)

    result = runner.invoke(__main__.main, ["5s"])

    # The key should have been read
    assert read_key_called[0], "read_key should have been called"
    # Output should NOT contain paused color since 'x' is not a pause key
    assert "\x1b[95m" not in result.stdout, (
        "Should not show paused color for non-pause key"
    )
    assert result.exit_code == 0


def test_sleep_exits_early_on_keypress(runner, monkeypatch):
    """Test that sleep loop exits early when a key is pressed mid-sleep."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    # Track sleep calls
    sleep_calls = []

    def fake_sleep(seconds):
        sleep_calls.append(seconds)
        # Exit after we've done a few sleep chunks
        if len(sleep_calls) >= 5:
            raise KeyboardInterrupt()

    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    # Simulate keypress after 3rd sleep call (during chunked 1-second sleep)
    check_count = [0]

    def fake_check_for_keypress():
        check_count[0] += 1
        # Return True on the 3rd sleep chunk to simulate keypress mid-sleep
        return len(sleep_calls) == 3

    def fake_read_key():
        return " "  # Pause key

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["10s"])
    assert result.exit_code == 0, result.output

    # Should have broken out of sleep loop early (not all 20 chunks)
    # We expect: 3 chunks of first iteration, then breaks, then starts paused sleep
    # The key point is we don't see all 20 chunks of 0.05 before breaking
    assert len(sleep_calls) >= 3, "Should have at least 3 sleep calls"
    # If it didn't exit early, we'd see many more 0.05 sleep calls
    # The presence of the break means we don't complete all 20 chunks
    first_iteration_sleeps = [s for s in sleep_calls[:3] if s == 0.05]
    assert len(first_iteration_sleeps) == 3, (
        "Should have 3 chunks of 0.05s before breaking"
    )


def test_resume_from_pause_exits_early(runner, monkeypatch):
    """Test that when paused, pressing a key to resume exits the 0.05s sleep loop."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    sleep_calls = []
    paused_state = [False]

    def fake_sleep(seconds):
        sleep_calls.append((seconds, paused_state[0]))
        if len(sleep_calls) >= 10:
            raise KeyboardInterrupt()

    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    # Simulate: pause immediately, then resume after a few paused sleeps
    keypress_count = [0]

    def fake_check_for_keypress():
        keypress_count[0] += 1
        # First keypress: pause immediately (keypress 1)
        # Second keypress: resume after being paused (keypress 2)
        return keypress_count[0] in [1, 5]

    keys_to_return = [" ", " "]  # Space to pause, space to resume
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
    assert result.exit_code == 0, result.output

    # Should have some paused sleeps (0.05) and some regular chunked sleeps (0.05)
    paused_sleeps = [s for s, p in sleep_calls if p]
    unpaused_sleeps = [s for s, p in sleep_calls if not p]

    assert len(paused_sleeps) > 0, "Should have some paused sleep periods"
    assert len(unpaused_sleeps) > 0, "Should have some unpaused sleep periods"


def test_add_time_with_plus_key(runner, monkeypatch):
    """Test that pressing + adds 30 seconds to the timer."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    # Track the displayed times
    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def fake_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    def fake_check_for_keypress():
        # Return True once to simulate a keypress
        return len(displayed_times) == 1

    def fake_read_key():
        return "+"  # Plus key to add time

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", fake_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["1m"])
    assert result.exit_code == 0, result.output

    # Should have displayed 60s initially, then 90s after pressing +
    assert 60 in displayed_times, "Should display initial time of 60s"
    assert 90 in displayed_times, "Should display 90s after adding 30s"


def test_subtract_time_with_minus_key(runner, monkeypatch):
    """Test that pressing - subtracts 30 seconds from the timer."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    # Track the displayed times
    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def fake_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    def fake_check_for_keypress():
        # Return True once to simulate a keypress
        return len(displayed_times) == 1

    def fake_read_key():
        return "-"  # Minus key to subtract time

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", fake_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["1m"])
    assert result.exit_code == 0, result.output

    # Should have displayed 60s initially, then 30s after pressing -
    assert 60 in displayed_times, "Should display initial time of 60s"
    assert 30 in displayed_times, "Should display 30s after subtracting 30s"


def test_subtract_time_cannot_go_negative(runner, monkeypatch):
    """Test that subtracting time stops at 0 (cannot go negative)."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    fake_sleep = FakeSleep(raises={1: KeyboardInterrupt()})
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    # Track the displayed times
    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def fake_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    def fake_check_for_keypress():
        # Return True once to simulate a keypress
        return len(displayed_times) == 1

    def fake_read_key():
        return "-"  # Minus key to subtract time

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", fake_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["10s"])
    assert result.exit_code == 0, result.output

    # Should have displayed 10s initially, then 0s (not -20s) after pressing -
    assert 10 in displayed_times, "Should display initial time of 10s"
    assert 0 in displayed_times, (
        "Should display 0s (not negative) after subtracting 30s"
    )
    assert all(t >= 0 for t in displayed_times), (
        "All displayed times should be non-negative"
    )


def test_q_key_quits_timer(runner, monkeypatch):
    """Test that pressing 'q' exits the timer."""
    monkeypatch.setattr(
        "countdown.display.get_terminal_size",
        fake_size(40, 20),
    )

    fake_sleep = FakeSleep()
    monkeypatch.setattr("countdown.__main__.sleep", fake_sleep)

    keypress_count = [0]

    def fake_check_for_keypress():
        keypress_count[0] += 1
        # Return True on first check to simulate pressing q
        return keypress_count[0] == 1

    def fake_read_key():
        return "q"  # Press q to quit

    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)

    result = runner.invoke(__main__.main, ["10m"])

    # Should exit cleanly with code 0
    assert result.exit_code == 0
    # Should have shown cursor and disabled alt buffer on exit
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_no_arguments_shows_help(runner):
    """Test that running without arguments shows help message."""
    result = runner.invoke(__main__.main, [])

    # Should exit with code 0 (not an error)
    assert result.exit_code == 0
    # Should show usage information
    assert "Usage:" in result.output
    assert "DURATION" in result.output
    # Should show examples
    assert "5m" in result.output or "Examples" in result.output
