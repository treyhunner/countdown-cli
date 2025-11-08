"""Command-line interface."""

import time

import click

from . import timer
from .display import (
    DISABLE_ALT_BUFFER,
    ENABLE_ALT_BUFFER,
    HIDE_CURSOR,
    SHOW_CURSOR,
    enable_ansi_escape_codes,
    get_chars_for_terminal,
    print_full_screen,
)
from .keys import get_time_adjustment, is_pause_key, is_time_adjust_key
from .terminal import (
    check_for_keypress,
    drain_keypresses,
    read_key,
    restore_terminal,
    setup_terminal,
)


def get_number_lines(seconds):
    """Return list of lines which make large MM:SS glyphs for given seconds."""
    return timer.get_number_lines(seconds, get_chars_for_terminal())


def run_countdown(total_seconds):
    """Run the countdown timer for the specified duration.

    Args:
        total_seconds: Duration in seconds to count down from
    """
    enable_ansi_escape_codes()
    old_settings = setup_terminal()
    print(ENABLE_ALT_BUFFER + HIDE_CURSOR, end="")
    try:
        paused = False
        n = total_seconds
        while n >= 0:
            lines = get_number_lines(n)
            print_full_screen(lines, paused=paused)

            # Check for keypress to toggle pause or adjust time
            if check_for_keypress():
                key = read_key()  # Consume the keypress

                if key == "q":
                    # Quit the timer
                    break
                elif is_pause_key(key):
                    paused = not paused
                    drain_keypresses()  # Ignore any additional rapid keypresses
                    lines = get_number_lines(n)
                    print_full_screen(lines, paused=paused)
                elif is_time_adjust_key(key):
                    # Adjust the timer by +/- 30 seconds
                    adjustment = get_time_adjustment(key)
                    n = max(0, n + adjustment)  # Don't go below 0
                    drain_keypresses()  # Ignore any additional rapid keypresses
                    lines = get_number_lines(n)
                    print_full_screen(lines, paused=paused)

            # Only sleep and decrement if not paused
            if not paused:
                # Sleep in small chunks to check for keypresses more frequently
                for _ in range(20):  # 20 x 0.05 = 1 second
                    time.sleep(0.05)
                    if check_for_keypress():
                        break  # Exit sleep early if key is pressed
                n -= 1
            else:
                # Short sleep when paused for responsive keypress checking
                time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        restore_terminal(old_settings)
        print(SHOW_CURSOR + DISABLE_ALT_BUFFER, end="")


@click.command()
@click.version_option(package_name="countdown-cli")
@click.argument("duration", type=timer.duration, required=False)
@click.pass_context
def main(ctx, duration):
    """Countdown from the given duration to 0.

    DURATION should be a number followed by m or s for minutes or seconds.

    Examples of DURATION:

    \\b
    - 5m (5 minutes)
    - 45s (45 seconds)
    - 2m30s (2 minutes and 30 seconds)

    Press Space, p, k, or Enter to pause/resume the countdown.

    Press +/= to add 30 seconds, - to subtract 30 seconds.

    Press q to quit.
    """  # noqa: D301
    # Show help if no duration provided
    if duration is None:
        click.echo(ctx.get_help())
        return

    run_countdown(duration)


if __name__ == "__main__":
    main(prog_name="countdown")  # pragma: no cover
