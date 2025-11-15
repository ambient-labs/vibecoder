"""Main codespace setup orchestration."""

import sys
import time
import traceback
from typing import Optional

from .codespace import (
    create_codespace,
    delete_codespace,
    find_codespace,
    wait_for_codespace_ready,
)
from .command import run_command
from .terminal import clear_screen, hide_cursor, show_cursor, status


def setup_codespace(
    repo: str,
    branch: str,
    machine: str,
    prompt: Optional[str] = None,
) -> None:
    """
    Complete setup flow: create codespace and connect to it.

    Args:
        repo: Repository in format 'owner/repo'.
        branch: Branch name to use.
        machine: Machine type (e.g., 'basicLinux32gb').
        prompt: Optional prompt (currently unused).
    """
    codespace_name: Optional[str] = None
    codespace_deleted = False
    try:
        clear_screen()
        hide_cursor()

        create_codespace(repo, branch, machine)

        # Retry finding codespace a few times in case it takes a moment to appear
        codespace_name = None
        for attempt in range(5):
            codespace_name = find_codespace(repo)
            if codespace_name:
                break
            if attempt < 4:
                status(f"🔍 Retrying to find codespace... (attempt {attempt + 1}/5)")
                time.sleep(2)
        
        if not codespace_name:
            sys.stdout.write("\r\033[K❌ Failed to get codespace name after multiple attempts\n")
            show_cursor()
            sys.exit(1)

        status(f"✅ Found codespace: {codespace_name}")

        if not wait_for_codespace_ready(codespace_name):
            sys.stdout.write("\r\033[K❌ Codespace did not become ready in time\n")
            show_cursor()
            sys.exit(1)

        status("✅ Setup complete!")
        time.sleep(1)

        # SSH into the codespace
        status("🔌 Connecting to codespace...")
        sys.stdout.write("\r\033[K")  # Clear status line
        show_cursor()

        # SSH is an interactive command - don't check exit code as user may exit normally
        try:
            run_command(
                [
                    "gh",
                    "codespace",
                    "ssh",
                    "-c",
                    codespace_name,
                ],
                check=False,  # Don't fail if SSH exits (user may disconnect)
            )
        except Exception as ssh_error:
            # SSH connection errors are expected in some cases
            sys.stdout.write(f"\r\033[K⚠️  SSH connection ended: {ssh_error}\n")
        finally:
            # Always clean up codespace after SSH session ends
            if codespace_name and not codespace_deleted:
                delete_codespace(codespace_name)
                codespace_deleted = True

    except KeyboardInterrupt:
        sys.stdout.write("\n")
        show_cursor()
        # Clean up codespace before exiting (if not already cleaned up)
        if codespace_name and not codespace_deleted:
            delete_codespace(codespace_name)
            codespace_deleted = True
        sys.exit(0)
    except Exception as e:
        sys.stdout.write(f"\r\033[K❌ Error: {e}\n")
        sys.stdout.write(f"Traceback: {traceback.format_exc()}\n")
        show_cursor()
        # Clean up codespace on error (if not already cleaned up)
        if codespace_name and not codespace_deleted:
            delete_codespace(codespace_name)
            codespace_deleted = True
        sys.exit(1)
