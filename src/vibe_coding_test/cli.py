"""CLI entry point for the vibe-coding-test package."""

import os
import sys
from typing import Optional

from dotenv import load_dotenv

from vibe_coding_test.main import setup_codespace


def main() -> None:
    """
    Main CLI entry point.
    
    Parses command-line arguments and environment variables,
    then runs the codespace setup flow.
    """
    # Load environment variables from .env if it exists
    load_dotenv()
    
    # Parse command-line arguments
    repo: str = sys.argv[1] if len(sys.argv) > 1 else "ambient-labs/vibe-coding-test"
    branch: str = sys.argv[2] if len(sys.argv) > 2 else "main"
    machine: str = sys.argv[3] if len(sys.argv) > 3 else "basicLinux32gb"
    prompt: Optional[str] = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Get API key from environment
    api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not set in .env or environment", file=sys.stderr)
        sys.exit(1)
    
    setup_codespace(repo, branch, machine, api_key, prompt)


if __name__ == "__main__":
    main()

