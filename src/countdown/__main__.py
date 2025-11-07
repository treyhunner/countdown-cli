"""Command-line interface."""

import re
import shutil
import sys
import time

import click

from .digits import CHARS_BY_SIZE, DIGIT_SIZES

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
        if size <= height and required_width <= width:
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
    """  # noqa: D301
    enable_ansi_escape_codes()
    print(ENABLE_ALT_BUFFER + HIDE_CURSOR, end="")
    try:
        for n in range(duration, -1, -1):
            lines = get_number_lines(n)
            print_full_screen(lines)
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        print(SHOW_CURSOR + DISABLE_ALT_BUFFER, end="")


def enable_ansi_escape_codes():
    """If running on Windows, enable ANSI escape codes."""
    if sys.platform == "win32":  # pragma: no cover
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


def print_full_screen(lines):
    """Print the given lines centered in the middle of the terminal window."""
    width, height = shutil.get_terminal_size()
    width -= max(len(line) for line in lines)
    height -= len(lines)
    vertical_pad = "\n" * (height // 2)
    padded_text = "\n".join(" " * (width // 2) + line for line in lines)
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
