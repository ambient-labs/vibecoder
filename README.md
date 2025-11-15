# Vibe Coding Test

A Python tool to create and manage GitHub Codespaces with Claude Code integration.

## Installation

This package uses [uv](https://github.com/astral-sh/uv) for fast dependency management.

### Install uv (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install the package

```bash
uv sync
```

Or install in development mode:

```bash
uv pip install -e .
```

## Configuration

Create a `.env` file in the project root with your Anthropic API key:

```
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

After installation, you can use the `vibe-setup` command:

```bash
vibe-setup [repo] [branch] [machine] [prompt]
```

### Arguments

- `repo` (optional): Repository in format `owner/repo` (default: `ambient-labs/vibe-coding-test`)
- `branch` (optional): Branch name (default: `main`)
- `machine` (optional): Machine type (default: `basicLinux32gb`)
- `prompt` (optional): Initial prompt to pass to Claude

### Examples

```bash
# Use defaults
vibe-setup

# Specify a different repository
vibe-setup myorg/myrepo

# Specify repository and branch
vibe-setup myorg/myrepo develop

# Specify all parameters
vibe-setup myorg/myrepo main basicLinux32gb "Help me debug this code"
```

## Development

### Run directly with uv

```bash
uv run python -m vibe_coding_test.cli
```

### Build and install

```bash
uv build
uv pip install dist/vibe_coding_test-*.whl
```

## Requirements

- Python 3.10+
- GitHub CLI (`gh`) installed and authenticated
- Anthropic API key

