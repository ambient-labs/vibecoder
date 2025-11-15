"""Terminal UI utilities."""

import os
import sys


def hide_cursor() -> None:
    """Hide the terminal cursor."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()


def show_cursor() -> None:
    """Show the terminal cursor."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("clear")


def status(message: str) -> None:
    """
    Print a status message, overwriting the current line.

    Args:
        message: The status message to display.
    """
    sys.stdout.write(f"\r\033[K{message}")
    sys.stdout.flush()

