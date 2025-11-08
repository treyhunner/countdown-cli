"""Keyboard input interpretation."""


def is_pause_key(key):
    """Check if the given key is a pause/resume key (Space, p, k, Enter)."""
    return key in (" ", "p", "k", "\r", "\n")


def is_time_adjust_key(key):
    """Check if the given key is a time adjustment key (+, =, -)."""
    return key in ("+", "=", "-")


def get_time_adjustment(key):
    """Return the time adjustment in seconds for the given key."""
    if key in ("+", "="):
        return 30  # Add 30 seconds
    elif key == "-":
        return -30  # Subtract 30 seconds
    return 0
