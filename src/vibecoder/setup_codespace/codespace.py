"""GitHub Codespace management operations."""

import re
import sys
import time
from typing import Optional

from .command import run_command
from .terminal import hide_cursor, show_cursor, status


def create_codespace(
    repo: str,
    branch: str,
    machine: str,
) -> None:
    """
    Create a new GitHub codespace.

    Args:
        repo: Repository in format 'owner/repo'.
        branch: Branch name to use.
        machine: Machine type (e.g., 'basicLinux32gb').
    """
    status(f"🚀 Creating codespace for {repo}...")

    run_command(
        [
            "gh",
            "codespace",
            "create",
            "-R",
            repo,
            "-b",
            branch,
            "-m",
            machine,
            "--idle-timeout",
            "5m",
            "--retention-period",
            "1h",
        ]
    )

    # Wait a bit for creation to register
    status("⏳ Waiting for codespace to register...")
    time.sleep(5)


def find_codespace(repo: str) -> Optional[str]:
    """
    Find the first available codespace for the given repository.
    Prioritizes Available codespaces, but will return the most recent one if none are available yet.

    Args:
        repo: Repository name to search for.

    Returns:
        Codespace name if found, None otherwise.
    """
    status("🔍 Finding codespace...")

    # Use -R flag to filter by repository
    result = run_command(
        ["gh", "codespace", "list", "-R", repo],
        capture_output=True,
    )

    lines = result.stdout.split("\n")
    available_codespace: Optional[str] = None
    first_codespace: Optional[str] = None

    for line in lines:
        # Skip header lines and empty lines
        if not line.strip() or line.startswith("NAME") or "---" in line:
            continue

        parts = line.split()
        if not parts:
            continue

        codespace_name = parts[0]

        # Store the first codespace we find (most recent)
        if first_codespace is None:
            first_codespace = codespace_name

        # Prioritize Available codespaces
        if "Available" in line or "available" in line.lower():
            available_codespace = codespace_name
            break

    # Return Available codespace if found, otherwise return the most recent one
    # (which should be the one we just created)
    return available_codespace or first_codespace


def wait_for_codespace_ready(codespace_name: str, max_attempts: int = 60) -> bool:
    """
    Wait for a codespace to become available.

    Args:
        codespace_name: Name of the codespace to wait for.
        max_attempts: Maximum number of attempts to check status.

    Returns:
        True if codespace is ready, False otherwise.

    Raises:
        KeyboardInterrupt: If interrupted by user.
    """
    status("⏳ Waiting for codespace to be ready...")

    for i in range(max_attempts):
        try:
            result = run_command(
                ["gh", "codespace", "view", "-c", codespace_name],
                check=False,
                capture_output=True,
            )

            # Extract state from output - try multiple patterns
            state = "Unknown"

            # First try: look for "State:" or "state:" with colon
            for line in result.stdout.split("\n"):
                if "state" in line.lower():
                    # Try various patterns
                    patterns = [
                        r"state:\s*(\w+)",  # state: Available
                        r"State:\s*(\w+)",  # State: Available
                        r"state\s+(\w+)",  # state Available
                        r"State\s+(\w+)",  # State Available
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            state = match.group(1)
                            break
                    if state != "Unknown":
                        break

            # If still unknown, try checking the list output directly
            if state == "Unknown":
                list_result = run_command(
                    ["gh", "codespace", "list", "-c", codespace_name],
                    check=False,
                    capture_output=True,
                )
                for line in list_result.stdout.split("\n"):
                    if codespace_name in line and (
                        "Available" in line or "available" in line.lower()
                    ):
                        # Extract state from list output (usually in a column)
                        parts = line.split()
                        for part in parts:
                            if part.lower() in [
                                "available",
                                "creating",
                                "shutting",
                                "stopped",
                            ]:
                                state = part
                                break
                        if state != "Unknown":
                            break

            attempt_num = i + 1
            status(
                f"⏳ Waiting for codespace to be ready... ({state}) [Attempt {attempt_num}/{max_attempts}]"
            )

            if state == "Available":
                status("✅ Codespace is ready!")
                time.sleep(1)
                return True

            time.sleep(5)
        except KeyboardInterrupt:
            raise
        except Exception:
            attempt_num = i + 1
            status(
                f"⏳ Waiting for codespace to be ready... (Error checking status) [Attempt {attempt_num}/{max_attempts}]"
            )
            time.sleep(5)

    return False


def delete_codespace(codespace_name: str) -> None:
    """
    Delete a codespace.

    Args:
        codespace_name: Name of the codespace to delete.
    """
    hide_cursor()
    status("🗑️  Deleting codespace...")

    run_command(
        [
            "gh",
            "codespace",
            "delete",
            "-c",
            codespace_name,
            "--force",
        ]
    )

    sys.stdout.write("\r\033[K✅ Codespace deleted\n")
    show_cursor()


def delete_all_codespaces() -> None:
    """
    Delete all active codespaces.
    """
    status("🔍 Finding all codespaces...")

    result = run_command(
        ["gh", "codespace", "list"],
        capture_output=True,
    )

    codespace_names: list[str] = []
    lines = result.stdout.split("\n")

    for line in lines:
        # Skip header lines and empty lines
        if not line.strip() or line.startswith("NAME") or "---" in line:
            continue

        parts = line.split()
        if parts:
            codespace_name = parts[0]
            codespace_names.append(codespace_name)

    if not codespace_names:
        status("✅ No codespaces found to delete")
        return

    status(f"🗑️  Deleting {len(codespace_names)} codespace(s)...")

    for i, codespace_name in enumerate(codespace_names, 1):
        status(f"🗑️  Deleting codespace {i}/{len(codespace_names)}: {codespace_name}...")
        try:
            run_command(
                [
                    "gh",
                    "codespace",
                    "delete",
                    "-c",
                    codespace_name,
                    "--force",
                ],
                check=False,  # Continue even if one fails
            )
        except Exception as e:
            sys.stdout.write(f"\r\033[K⚠️  Failed to delete {codespace_name}: {e}\n")

    sys.stdout.write(f"\r\033[K✅ Deleted {len(codespace_names)} codespace(s)\n")
    show_cursor()
