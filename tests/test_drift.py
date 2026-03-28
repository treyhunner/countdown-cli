"""Tests for drift correction in the countdown timer."""

from countdown import __main__


def test_countdown_displays_each_second(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Test that a 5-second countdown displays each second value."""
    fake_terminal_size(40, 20)

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    result = runner.invoke(__main__.main, ["5s"])
    assert result.exit_code == 0
    assert displayed_times == [5, 4, 3, 2, 1, 0]


def test_drift_correction_with_slow_sleeps(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """With drift, the timer still counts down the right number of seconds.

    Each 0.05s sleep takes 0.06s (simulating OS scheduling overhead).
    Without drift correction, this would make the countdown run 20% too long.
    With drift correction, each second still advances based on wall clock time.
    """
    fake_terminal_size(40, 20)
    fake_clock.drift_per_sleep = 0.01

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    result = runner.invoke(__main__.main, ["5s"])
    assert result.exit_code == 0

    # Even with drift, we should still display 5 seconds counting down
    assert displayed_times == [5, 4, 3, 2, 1, 0]


def test_drift_correction_skips_seconds_when_very_slow(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Simulate extreme drift.

    With extreme drift, individual seconds may be skipped but total time
    is still bounded by wall clock time, not by sleep iteration count.
    """
    fake_terminal_size(40, 20)
    # Each 0.05s sleep takes 0.55s (extreme drift: 10x)
    fake_clock.drift_per_sleep = 0.5

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    result = runner.invoke(__main__.main, ["60m"])
    assert result.exit_code == 0

    # Timer should still start at 60m and count down
    assert displayed_times[0] == 60 * 60
    # Each second is displayed for fewer sleep iterations due to drift,
    # but the total still counts down correctly (each displayed value
    # is less than the one before)
    for i in range(1, len(displayed_times)):
        assert displayed_times[i] < displayed_times[i - 1]


def test_pause_preserves_remaining_time(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Pausing and resuming should not consume countdown time."""
    fake_terminal_size(40, 20)

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    # Pause on first display, then resume after 3 checks while paused
    keypress_count = [0]

    def fake_check_for_keypress():
        keypress_count[0] += 1
        return keypress_count[0] in [1, 5]  # pause, then resume

    keys = iter([" ", " "])  # pause, resume

    def fake_read_key():
        return next(keys)

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["3s"])
    assert result.exit_code == 0

    # Despite pausing, all countdown seconds should still be displayed
    assert 3 in displayed_times
    assert 2 in displayed_times
    assert 1 in displayed_times


def test_add_time_extends_deadline(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Pressing + should extend the countdown deadline by 30 seconds."""
    fake_terminal_size(40, 20)
    fake_clock.raises = {5: KeyboardInterrupt()}

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    # Press + on first display
    def fake_check_for_keypress():
        return len(displayed_times) == 1

    def fake_read_key():
        return "+"

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["10s"])
    assert result.exit_code == 0

    # After pressing + on display of 10, n jumps to 40 (10+30)
    assert displayed_times[0] == 10
    assert 40 in displayed_times
    # Timer should count down from 40 (not restart from 10)
    idx_40 = displayed_times.index(40)
    assert displayed_times[idx_40 + 1] == 39


def test_subtract_time_shortens_deadline(
    runner,
    fake_terminal_size,
    fake_clock,
    monkeypatch,
):
    """Pressing - should shorten the countdown deadline by 30 seconds."""
    fake_terminal_size(40, 20)

    displayed_times = []
    original_get_number_lines = __main__.get_number_lines

    def tracking_get_number_lines(seconds):
        displayed_times.append(seconds)
        return original_get_number_lines(seconds)

    # Press - on first display
    def fake_check_for_keypress():
        return len(displayed_times) == 1

    def fake_read_key():
        return "-"

    def fake_drain():
        pass

    monkeypatch.setattr(__main__, "get_number_lines", tracking_get_number_lines)
    monkeypatch.setattr(__main__, "check_for_keypress", fake_check_for_keypress)
    monkeypatch.setattr(__main__, "read_key", fake_read_key)
    monkeypatch.setattr(__main__, "drain_keypresses", fake_drain)

    result = runner.invoke(__main__.main, ["1m"])
    assert result.exit_code == 0

    # After pressing - on display of 60, n drops to 30 (60-30)
    assert displayed_times[0] == 60
    assert 30 in displayed_times
    # Timer should end at 0 after counting down ~30 seconds (not ~60)
    assert displayed_times[-1] == 0
    # Total seconds displayed should be ~31 (30 down to 0, not 60 down to 0)
    assert len([t for t in displayed_times if t <= 30]) < 35
