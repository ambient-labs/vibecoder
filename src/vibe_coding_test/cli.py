"""CLI entry point for the vibe-coder package."""

import argparse
from typing import Optional

from dotenv import load_dotenv

from .setup_codespace import setup_codespace
from .setup_codespace.codespace import delete_all_codespaces


def main() -> None:
    """
    Main CLI entry point.

    Parses command-line arguments and environment variables,
    then runs the codespace setup flow.
    """
    # Load environment variables from .env if it exists
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Create and connect to a GitHub Codespace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--delete-all",
        action="store_true",
        help="Delete all active codespaces",
    )

    parser.add_argument(
        "repo",
        nargs="?",
        help="Repository in format 'owner/repo'",
    )

    parser.add_argument(
        "branch",
        nargs="?",
        default="main",
        help="Branch name to use (default: main)",
    )

    parser.add_argument(
        "machine",
        nargs="?",
        default="basicLinux32gb",
        help="Machine type (default: basicLinux32gb)",
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        default=None,
        help="Optional prompt (currently unused)",
    )

    args = parser.parse_args()

    if args.delete_all:
        delete_all_codespaces()
        return

    if not args.repo:
        parser.error("repo is required unless using --delete-all")

    setup_codespace(args.repo, args.branch, args.machine, args.prompt)


if __name__ == "__main__":
    main()
