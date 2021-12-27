"""Command-line interface."""
from __future__ import annotations

import re
import shutil
import sys
import time

import click


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

CHARS = {
    "0": "██████\n██  ██\n██  ██\n██  ██\n██████",
    "1": "   ██ \n  ███ \n   ██ \n   ██ \n   ██ ",
    "2": "██████\n    ██\n██████\n██    \n██████",
    "3": "██████\n    ██\n █████\n    ██\n██████",
    "4": "██  ██\n██  ██\n██████\n    ██\n    ██",
    "5": "██████\n██    \n██████\n    ██\n██████",
    "6": "██████\n██    \n██████\n██  ██\n██████",
    "7": "██████\n    ██\n   ██ \n  ██  \n  ██  ",
    "8": " ████ \n██  ██\n ████ \n██  ██\n ████ ",
    "9": "██████\n██  ██\n██████\n    ██\n █████",
    ":": "  \n██\n  \n██\n  ",
}
CLEAR = "\033[H\033[J"


def duration(string: str) -> int:
    """Convert given XmXs string to seconds (as an integer)."""
    match = DURATION_RE.search(string)
    if not match:
        raise ValueError(f"Invalid duration: {string}")
    minutes, seconds = match.groups()
    return int(minutes or 0) * 60 + int(seconds or 0)


@click.command()
@click.version_option(package_name="countdown-cli")
@click.argument("duration", type=duration)
def main(duration: int) -> None:
    """Countdown from the given duration to 0.

    DURATION should be a number followed by m or s for minutes or seconds.

    Examples of DURATION:

    \b
    - 5m (5 minutes)
    - 45s (30 seconds)
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


def enable_ansi_escape_codes() -> None:
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


def print_full_screen(lines: list[str]) -> None:
    """Print the given lines centered in the middle of the terminal window."""
    width, height = shutil.get_terminal_size()
    width -= max(len(line) for line in lines)
    height -= len(lines) + 2
    vertical_pad = "\n" * (height // 2)
    padded_text = "\n".join(" " * (width // 2) + line for line in lines)
    print(CLEAR + vertical_pad + padded_text, flush=True)


def get_number_lines(seconds: int) -> list[str]:
    """Return list of lines which make large MM:SS glyphs for given seconds."""
    lines = [""] * 5
    minutes, seconds = divmod(seconds, 60)
    time = f"{minutes:02d}:{seconds:02d}"
    for char in time:
        char_lines = CHARS[char].splitlines()
        for i, line in enumerate(char_lines):
            lines[i] += line + " "
    return lines


if __name__ == "__main__":
    main(prog_name="countdown")  # pragma: no cover
