"""Integration test cases for the CLI."""

import re

import pytest

from countdown import __main__


def clean_main_output(output):
    """Remove ANSI escape codes and whitespace at ends of lines."""
    output = re.sub(r"\033\[(\?\d+[hl]|[HJ])", "", output)
    output = re.sub(r" *\n", "\n", output)
    return output


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


def test_main_3_seconds(runner, fake_terminal_size, fake_clock):
    # Use 40x20 terminal to select size 5 digits (33w <= 40, 5h+2 <= 20)
    fake_terminal_size(40, 20)
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
    # 3 seconds + 1 to display 00:00, each sleeping ~1 second
    assert fake_clock.slept == pytest.approx(3 + 1, abs=0.01)
    assert fake_clock.elapsed == pytest.approx(3 + 1, abs=0.01)


def test_main_1_minute(runner, fake_terminal_size, fake_clock):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
    fake_terminal_size(40, 10)

    # Raise exception after 11 seconds of fake sleep
    fake_clock.raises = {11: SystemExit(0)}

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


def test_main_10_minutes_has_600_clear_screens(
    runner,
    fake_terminal_size,
    fake_clock,
):
    fake_terminal_size(32, 10)
    result = runner.invoke(__main__.main, ["10m"])
    # 10 minutes = 600 seconds + 1 to display 00:00
    assert fake_clock.slept == pytest.approx(10 * 60 + 1, abs=0.1)
    assert fake_clock.elapsed == pytest.approx(10 * 60 + 1, abs=0.1)
    assert result.stdout.count("\033[H\033[J") == 10 * 60 + 1


def test_main_enables_alt_buffer_and_hides_cursor_at_beginning(
    runner,
    fake_terminal_size,
    fake_clock,
):
    fake_terminal_size(32, 10)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.startswith("\033[?1049h\033[?25l")


def test_main_disable_alt_buffer_and_show_cursor_at_end(
    runner,
    fake_terminal_size,
    fake_clock,
):
    fake_terminal_size(32, 10)
    result = runner.invoke(__main__.main, ["5m"])
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_main_early_exit_still_shows_cursor_at_end(
    runner,
    fake_terminal_size,
    fake_clock,
):
    # Use 40x10 terminal to select size 5 digits (33w <= 40, 5h+2 <= 10)
    fake_terminal_size(40, 10)

    # Hit Ctrl+C after 4 seconds total sleep time (chunked sleep)
    fake_clock.raises = {4: KeyboardInterrupt()}

    result = runner.invoke(__main__.main, ["15m"])
    # 4 seconds of sleep = 4 iterations, each printing 5 lines + 1 padding line
    # except the last which has no trailing padding = 4*6-1 = 23 lines,
    # plus 2 lines vertical padding for 10-line terminal = 25 lines
    assert len(result.stdout.splitlines()) == 25
    assert result.stdout.endswith("\033[?25h\033[?1049l")


def test_pause_key_triggers_pause(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that pressing a pause key triggers the pause logic."""
    fake_terminal_size(40, 20)

    # Exit after a short time
    fake_clock.raises = {1: KeyboardInterrupt()}

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


def test_non_pause_key_ignored(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that non-pause keys are ignored during countdown."""
    fake_terminal_size(40, 20)
    fake_clock.raises = {1: KeyboardInterrupt()}

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


def test_sleep_exits_early_on_keypress(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that sleep loop exits early when a key is pressed mid-sleep."""
    fake_terminal_size(40, 20)

    # Track sleep calls and use FakeClock for time control
    sleep_calls = []
    original_sleep = fake_clock.sleep

    def tracking_sleep(seconds):
        sleep_calls.append(seconds)
        original_sleep(seconds)
        if len(sleep_calls) >= 5:
            raise KeyboardInterrupt()

    monkeypatch.setattr("countdown.__main__.sleep", tracking_sleep)

    # Simulate keypress after 3rd sleep call (during chunked 1-second sleep)
    def fake_check_for_keypress():
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
    assert len(sleep_calls) >= 3, "Should have at least 3 sleep calls"
    first_iteration_sleeps = [s for s in sleep_calls[:3] if s == 0.05]
    assert len(first_iteration_sleeps) == 3, (
        "Should have 3 chunks of 0.05s before breaking"
    )


def test_resume_from_pause_exits_early(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that when paused, pressing a key to resume exits the 0.05s sleep loop."""
    fake_terminal_size(40, 20)

    sleep_calls = []
    paused_state = [False]
    original_sleep = fake_clock.sleep

    def tracking_sleep(seconds):
        sleep_calls.append((seconds, paused_state[0]))
        original_sleep(seconds)
        if len(sleep_calls) >= 10:
            raise KeyboardInterrupt()

    monkeypatch.setattr("countdown.__main__.sleep", tracking_sleep)

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


def test_add_time_with_plus_key(
    runner, fake_terminal_size, fake_clock, monkeypatch
):
    """Test that pressing + adds 30 seconds to the timer."""
    fake_terminal_size(40, 20)
    fake_clock.raises = {1: KeyboardInterrupt()}

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


def test_subtract_time_with_minus_key(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that pressing - subtracts 30 seconds from the timer."""
    fake_terminal_size(40, 20)
    fake_clock.raises = {1: KeyboardInterrupt()}

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


def test_subtract_time_cannot_go_negative(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that subtracting time stops at 0 (cannot go negative)."""
    fake_terminal_size(40, 20)
    fake_clock.raises = {1: KeyboardInterrupt()}

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


def test_q_key_quits_timer(runner, fake_terminal_size, fake_clock, monkeypatch):
    """Test that pressing 'q' exits the timer."""
    fake_terminal_size(40, 20)
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
