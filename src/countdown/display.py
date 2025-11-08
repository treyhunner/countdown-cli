"""Visual rendering and ANSI terminal control."""

import shutil
import sys

from .digits import CHARS_BY_SIZE, DIGIT_SIZES

# ANSI escape codes for terminal control
ENABLE_ALT_BUFFER = "\033[?1049h"
DISABLE_ALT_BUFFER = "\033[?1049l"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR = "\033[H\033[J"

# ANSI color codes
INTENSE_MAGENTA = "\x1b[95m"
RESET = "\033[0m"


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
