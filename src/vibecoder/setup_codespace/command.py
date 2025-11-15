"""Command execution utilities."""

import os
import subprocess


def run_command(
    command: list[str],
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess[str]:
    """
    Run a shell command and return the result.

    Args:
        command: List of command arguments.
        check: Whether to raise an exception on non-zero exit code.
        capture_output: Whether to capture stdout and stderr.

    Returns:
        CompletedProcess with command result.

    Raises:
        subprocess.CalledProcessError: If check is True and command fails.
    """
    env = os.environ.copy()
    # Add common Homebrew paths for Apple Silicon Macs
    homebrew_paths = "/opt/homebrew/bin:/usr/local/bin"
    env["PATH"] = f"{homebrew_paths}:{env.get('PATH', '')}"

    return subprocess.run(
        command,
        check=check,
        capture_output=capture_output,
        text=True,
        env=env,
    )

