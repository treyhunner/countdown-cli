"""Platform-specific terminal and keyboard I/O operations."""
# pragma: no cover

import sys

if sys.platform == "win32":  # pragma: no cover
    import msvcrt
else:  # pragma: no cover
    import select
    import termios
    import tty


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
        key = msvcrt.getch()
    else:
        key = sys.stdin.read(1)

    # Convert bytes to string if needed (Windows returns bytes)
    if isinstance(key, bytes):
        key = key.decode("utf-8", errors="ignore")
    return key


def drain_keypresses():  # pragma: no cover
    """Consume all pending keypresses from the input buffer."""
    while check_for_keypress():
        read_key()


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
