"""Utilities for generating large digits."""

from importlib.resources import files
from itertools import zip_longest

DIGIT_SIZES = []
CHARS_BY_SIZE = {}


def paragraphs(lines):
    """Return groups of non-blank lines."""
    group = []
    for line in lines:
        if line.strip():
            group.append(line)
        elif group:
            yield group
            group = []
    yield group


def transpose(lines):
    """Transpose a list of strings (columns become rows)."""
    return ("".join(column) for column in zip_longest(*lines, fillvalue=" "))


def center(text, width):
    """Center text so that each line will have the given width."""
    return "\n".join(f"{line:^{width}}" for line in text.splitlines())


def populate_constants():
    """Populate CHARS_BY_SIZE and DIGIT_SIZES to contain the numbers in numbers.txt."""
    lines = files("countdown").joinpath("numbers.txt").read_text().splitlines()
    number_types = list(paragraphs(lines))
    for group in number_types:
        columns = transpose(group)
        numbers = ["\n".join(transpose(p)) for p in paragraphs(columns)]
        heights = [len(n.splitlines()) for n in numbers]
        widths = [max(len(line) for line in n.splitlines()) for n in numbers]
        max_width = max(widths)
        [height] = set(heights)
        DIGIT_SIZES.append(height)
        chars = CHARS_BY_SIZE[height] = {}
        for digit, text in enumerate(numbers, start=-1):
            if digit == -1:
                colon_width = max(len(line) for line in text.splitlines())
                chars[":"] = (
                    center(text, colon_width + 2)  # 2 spaces around :
                    if len(text) > 1
                    else text
                )
            else:
                chars[str(digit)] = center(text, max_width)
    DIGIT_SIZES.sort(reverse=True)


populate_constants()
