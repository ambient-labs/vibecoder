"""Main module for codespace management."""

import os
import re
import subprocess
import sys
import time
from typing import Optional


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
    
    run_command([
        "gh",
        "codespace",
        "create",
        "-R", repo,
        "-b", branch,
        "-m", machine,
        "--idle-timeout", "5m",
        "--retention-period", "1h",
    ])
    
    # Wait a bit for creation to register
    status("⏳ Waiting for codespace to register...")
    time.sleep(5)


def find_codespace(repo: str) -> Optional[str]:
    """
    Find the first available codespace for the given repository.
    
    Args:
        repo: Repository name to search for.
        
    Returns:
        Codespace name if found, None otherwise.
    """
    status("🔍 Finding codespace...")
    
    result = run_command(
        ["gh", "codespace", "list"],
        capture_output=True,
    )
    
    lines = result.stdout.split("\n")
    for line in lines:
        if repo in line and "Available" in line:
            # Extract codespace name (first field)
            parts = line.split()
            if parts:
                return parts[0]
    
    return None


def wait_for_codespace_ready(codespace_name: str, max_attempts: int = 60) -> bool:
    """
    Wait for a codespace to become available.
    
    Args:
        codespace_name: Name of the codespace to wait for.
        max_attempts: Maximum number of attempts to check status.
        
    Returns:
        True if codespace is ready, False otherwise.
    """
    status("⏳ Waiting for codespace to be ready...")
    
    for i in range(max_attempts):
        try:
            result = run_command(
                ["gh", "codespace", "view", "-c", codespace_name],
                check=False,
                capture_output=True,
            )
            
            # Extract state from output
            state = "Unknown"
            for line in result.stdout.split("\n"):
                if "state" in line.lower():
                    match = re.search(r"state:\s*(\w+)", line, re.IGNORECASE)
                    if match:
                        state = match.group(1)
                        break
            
            status(f"⏳ Waiting for codespace to be ready... ({state})")
            
            if state == "Available":
                status("✅ Codespace is ready!")
                time.sleep(1)
                return True
            
            time.sleep(5)
        except Exception:
            time.sleep(5)
    
    return False


def install_claude_code(codespace_name: str) -> None:
    """
    Install Claude Code in the codespace.
    
    Args:
        codespace_name: Name of the codespace.
    """
    status("🔧 Installing Claude Code...")
    
    install_script = "curl -fsSL https://claude.ai/install.sh | bash"
    
    run_command([
        "gh",
        "codespace",
        "ssh",
        "-c", codespace_name,
        "--",
        "bash",
        "-c",
        f"set -e; {install_script}",
    ])


def configure_api_key(codespace_name: str, api_key: str) -> None:
    """
    Configure the Anthropic API key in the codespace.
    
    Args:
        codespace_name: Name of the codespace.
        api_key: The Anthropic API key.
    """
    status("🔑 Configuring API key...")
    
    # Escape the API key for shell usage
    escaped_key = api_key.replace("'", "'\"'\"'")
    
    config_script = f"""
    echo 'export ANTHROPIC_API_KEY="{escaped_key}"' >> ~/.bashrc
    echo 'export ANTHROPIC_API_KEY="{escaped_key}"' >> ~/.profile
    echo 'export ANTHROPIC_API_KEY="{escaped_key}"' >> ~/.bash_profile
    export ANTHROPIC_API_KEY="{escaped_key}"
    """
    
    run_command([
        "gh",
        "codespace",
        "ssh",
        "-c", codespace_name,
        "--",
        "bash",
        "-c",
        config_script,
    ])


def verify_api_key(codespace_name: str) -> bool:
    """
    Verify that the API key is set in the codespace.
    
    Args:
        codespace_name: Name of the codespace.
        
    Returns:
        True if API key is verified, False otherwise.
    """
    status("🔍 Verifying API key...")
    
    result = run_command(
        [
            "gh",
            "codespace",
            "ssh",
            "-c", codespace_name,
            "--",
            "bash",
            "-c",
            "source ~/.bashrc && [ -n \"$ANTHROPIC_API_KEY\" ] && echo 'API key verified' || echo 'API key not found'",
        ],
        capture_output=True,
    )
    
    return "verified" in result.stdout.lower()


def start_claude(codespace_name: str, api_key: str, prompt: Optional[str] = None) -> None:
    """
    Start Claude Code in the codespace.
    
    Args:
        codespace_name: Name of the codespace.
        api_key: The Anthropic API key.
        prompt: Optional prompt to pass to Claude.
    """
    status("✨ Starting Claude Code...")
    sys.stdout.write("\r\033[K")  # Clear status line
    show_cursor()
    
    escaped_key = api_key.replace("'", "'\"'\"'")
    
    claude_command = (
        "source ~/.bashrc && source ~/.profile && "
        f"export ANTHROPIC_API_KEY='{escaped_key}' && "
        "cd /workspaces/* 2>/dev/null || cd ~ && "
    )
    
    if prompt:
        escaped_prompt = prompt.replace("'", "'\"'\"'")
        claude_command += f"claude -p '{escaped_prompt}'"
    else:
        claude_command += "exec claude"
    
    run_command([
        "gh",
        "codespace",
        "ssh",
        "-c", codespace_name,
        "--",
        "-t",
        "env",
        f"ANTHROPIC_API_KEY={api_key}",
        "bash",
        "-c",
        claude_command,
    ])


def delete_codespace(codespace_name: str) -> None:
    """
    Delete a codespace.
    
    Args:
        codespace_name: Name of the codespace to delete.
    """
    hide_cursor()
    status("🗑️  Deleting codespace...")
    
    run_command([
        "gh",
        "codespace",
        "delete",
        "-c", codespace_name,
        "--force",
    ])
    
    sys.stdout.write("\r\033[K✅ Codespace deleted\n")
    show_cursor()


def setup_codespace(
    repo: str,
    branch: str,
    machine: str,
    api_key: str,
    prompt: Optional[str] = None,
) -> None:
    """
    Complete setup flow: create, configure, and start Claude in a codespace.
    
    Args:
        repo: Repository in format 'owner/repo'.
        branch: Branch name to use.
        machine: Machine type (e.g., 'basicLinux32gb').
        api_key: The Anthropic API key.
        prompt: Optional prompt to pass to Claude.
    """
    try:
        clear_screen()
        hide_cursor()
        
        create_codespace(repo, branch, machine)
        
        codespace_name = find_codespace(repo)
        if not codespace_name:
            sys.stdout.write("\r\033[K❌ Failed to get codespace name\n")
            show_cursor()
            sys.exit(1)
        
        status(f"✅ Found codespace: {codespace_name}")
        
        if not wait_for_codespace_ready(codespace_name):
            sys.stdout.write("\r\033[K❌ Codespace did not become ready in time\n")
            show_cursor()
            sys.exit(1)
        
        install_claude_code(codespace_name)
        configure_api_key(codespace_name, api_key)
        
        if not verify_api_key(codespace_name):
            sys.stdout.write("\r\033[K⚠️  API key verification failed, but continuing...\n")
        
        status("✅ Setup complete!")
        time.sleep(1)
        
        start_claude(codespace_name, api_key, prompt)
        
    except KeyboardInterrupt:
        sys.stdout.write("\n")
        show_cursor()
        raise
    except Exception as e:
        sys.stdout.write(f"\r\033[K❌ Error: {e}\n")
        show_cursor()
        sys.exit(1)
    finally:
        # Clean up codespace if we have the name
        if "codespace_name" in locals():
            delete_codespace(codespace_name)

