"""Command-line interface."""

import re
import shutil
import sys
import time

import click

from .digits import CHARS_BY_SIZE, DIGIT_SIZES

if sys.platform == "win32":  # pragma: no cover
    import msvcrt
else:  # pragma: no cover
    import select
    import termios
    import tty

ENABLE_ALT_BUFFER = "\033[?1049h"
DISABLE_ALT_BUFFER = "\033[?1049l"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"

DURATION_RE = re.compile(
    r"""
    ^
    (?:                 # Optional minutes
        ( \d{1,2} )     # D or DD
        m               # "m"
    )?
    (?:                 # Optional seconds
        ( \d{1,2} )     # D or DD
        s               # "s"
    )?
    $
""",
    re.VERBOSE,
)

CLEAR = "\033[H\033[J"
INTENSE_MAGENTA = "\x1b[95m"
RESET = "\033[0m"


def check_for_keypress():  # pragma: no cover
    """Check if a key has been pressed (non-blocking)."""
    if not sys.stdin.isatty():
        return False
    if sys.platform == "win32":
        return msvcrt.kbhit()
    else:
        return select.select([sys.stdin], [], [], 0)[0]


def read_key():  # pragma: no cover
    """Read a single keypress."""
    if sys.platform == "win32":
        return msvcrt.getch()
    else:
        return sys.stdin.read(1)


def drain_keypresses():  # pragma: no cover
    """Consume all pending keypresses from the input buffer."""
    while check_for_keypress():
        read_key()


def is_pause_key(key):
    """Check if the given key is a pause/resume key (Space, p, k, Enter)."""
    # Handle both bytes (Windows) and strings (Unix)
    if isinstance(key, bytes):
        key = key.decode("utf-8", errors="ignore")
    return key in (" ", "p", "k", "\r", "\n")


def is_time_adjust_key(key):
    """Check if the given key is a time adjustment key (+, =, -)."""
    # Handle both bytes (Windows) and strings (Unix)
    if isinstance(key, bytes):
        key = key.decode("utf-8", errors="ignore")
    return key in ("+", "=", "-")


def get_time_adjustment(key):
    """Return the time adjustment in seconds for the given key."""
    # Handle both bytes (Windows) and strings (Unix)
    if isinstance(key, bytes):
        key = key.decode("utf-8", errors="ignore")
    if key in ("+", "="):
        return 30  # Add 30 seconds
    elif key == "-":
        return -30  # Subtract 30 seconds
    return 0


def setup_terminal():  # pragma: no cover
    """Setup terminal for non-blocking input (Unix only)."""
    if sys.platform != "win32" and sys.stdin.isatty():
        try:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            tty.setcbreak(fd)
            return old_settings
        except (termios.error, OSError):
            pass
    return None


def restore_terminal(old_settings):  # pragma: no cover
    """Restore terminal settings (Unix only)."""
    if sys.platform != "win32" and old_settings:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def get_required_width(chars):
    """Calculate the minimum width required to display MM:SS format."""
    # MM:SS format has 4 digits, 1 colon, and 1 space after each char
    digit_width = max(len(line) for line in chars["0"].splitlines())
    colon_width = max(len(line) for line in chars[":"].splitlines())
    # Total: 4 digits + 1 colon + 5 spaces (after each character)
    return digit_width * 4 + colon_width + 5


def get_chars_for_terminal():
    """Return the largest CHARS dictionary that fits in the current terminal."""
    width, height = shutil.get_terminal_size()
    for size in DIGIT_SIZES:
        chars = CHARS_BY_SIZE[size]
        required_width = get_required_width(chars)
        # For size 3 (smallest multi-line), allow it without padding
        # For larger sizes, require 1 line of padding on top and bottom (2 total)
        padding_needed = 0 if size == 3 else 2
        if size + padding_needed <= height and required_width <= width:
            return chars
    # If terminal is too small, return the smallest available
    return CHARS_BY_SIZE[min(DIGIT_SIZES)]


def duration(string):
    """Convert given XmXs string to seconds (as an integer)."""
    match = DURATION_RE.search(string)
    if not match:
        raise ValueError(f"Invalid duration: {string}")
    minutes, seconds = match.groups()
    return int(minutes or 0) * 60 + int(seconds or 0)


@click.command()
@click.version_option(package_name="countdown-cli")
@click.argument("duration", type=duration)
def main(duration):
    """Countdown from the given duration to 0.

    DURATION should be a number followed by m or s for minutes or seconds.

    Examples of DURATION:

    \b
    - 5m (5 minutes)
    - 45s (45 seconds)
    - 2m30s (2 minutes and 30 seconds)

    Press Space, p, k, or Enter to pause/resume the countdown.
    Press +/= to add 30 seconds, - to subtract 30 seconds.
    """  # noqa: D301
    enable_ansi_escape_codes()
    old_settings = setup_terminal()
    print(ENABLE_ALT_BUFFER + HIDE_CURSOR, end="")
    try:
        paused = False
        n = duration
        while n >= 0:
            lines = get_number_lines(n)
            print_full_screen(lines, paused=paused)

            # Check for keypress to toggle pause or adjust time
            if check_for_keypress():
                key = read_key()  # Consume the keypress
                if is_pause_key(key):
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


def enable_ansi_escape_codes():  # pragma: no cover
    """If running on Windows, enable ANSI escape codes."""
    if sys.platform == "win32":
        from ctypes import windll

        k = windll.kernel32
        stdout = -11
        enable_processed_output = 0x0001
        enable_wrap_at_eol_output = 0x0002
        enable_virtual_terminal_processing = 0x0004
        k.SetConsoleMode(
            k.GetStdHandle(stdout),
            enable_processed_output
            | enable_wrap_at_eol_output
            | enable_virtual_terminal_processing,
        )


def print_full_screen(lines, paused=False):
    """Print the given lines centered in the middle of the terminal window."""
    term_width, term_height = shutil.get_terminal_size()

    # Calculate total content height
    content_height = len(lines)
    show_pause_text = False
    if paused and content_height + 2 <= term_height:
        # Only show PAUSED text if there's room
        content_height += 2  # Blank line + PAUSED text
        show_pause_text = True

    # Calculate vertical padding (ensure it doesn't go negative)
    vertical_padding = max(0, (term_height - content_height) // 2)

    # Calculate horizontal padding for timer
    max_line_width = max(len(line) for line in lines)
    horizontal_padding = max(0, (term_width - max_line_width) // 2)

    # Apply red color to timer if paused
    if paused:
        colored_lines = [INTENSE_MAGENTA + line + RESET for line in lines]
    else:
        colored_lines = lines

    # Build the output
    vertical_pad = "\n" * vertical_padding
    padded_text = "\n".join(
        " " * horizontal_padding + line for line in colored_lines
    )

    if show_pause_text:
        pause_text = "PAUSED - Press any key to resume"
        pause_padding = " " * max(0, (term_width - len(pause_text)) // 2)
        padded_text += "\n\n" + pause_padding + pause_text

    print(CLEAR + vertical_pad + padded_text, flush=True, end="")


def get_number_lines(seconds):
    """Return list of lines which make large MM:SS glyphs for given seconds."""
    chars = get_chars_for_terminal()
    digit_height = len(next(iter(chars.values())).splitlines())
    lines = [""] * digit_height
    minutes, seconds = divmod(seconds, 60)
    time = f"{minutes:02d}:{seconds:02d}"
    for char in time:
        char_lines = chars[char].splitlines()
        for i, line in enumerate(char_lines):
            lines[i] += line + " "
    return lines


if __name__ == "__main__":
    main(prog_name="countdown")  # pragma: no cover
