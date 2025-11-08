"""Time parsing and formatting utilities."""

import re

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


def duration(string):
    """Convert given XmXs string to seconds (as an integer)."""
    match = DURATION_RE.search(string)
    if not match:
        raise ValueError(f"Invalid duration: {string}")
    minutes, seconds = match.groups()
    return int(minutes or 0) * 60 + int(seconds or 0)


def get_number_lines(seconds, chars):
    """Return list of lines which make large MM:SS glyphs for given seconds.

    Args:
        seconds: The time in seconds to format
        chars: Dictionary of character glyphs to use for rendering

    Returns:
        List of strings, one per line of the ASCII art display
    """
    digit_height = len(next(iter(chars.values())).splitlines())
    lines = [""] * digit_height
    minutes, seconds = divmod(seconds, 60)
    time = f"{minutes:02d}:{seconds:02d}"
    for char in time:
        char_lines = chars[char].splitlines()
        for i, line in enumerate(char_lines):
            lines[i] += line + " "
    return lines
