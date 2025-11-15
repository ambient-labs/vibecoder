#!/bin/bash
set -e

# Clear screen and set up for interactive updates
clear
printf "\033[?25l"  # Hide cursor

# Add common Homebrew paths to PATH (for Apple Silicon Macs)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

# Load environment variables from .env if it exists
if [ -f .env ]; then
  export $(grep -v '^#' .env | grep -v '^$' | xargs)
fi

REPO="${1:-ambient-labs/vibe-coding-test}"
BRANCH="${2:-main}"
MACHINE="${3:-basicLinux32gb}"
PROMPT="${4:-}"

status() {
  printf "\r\033[K%s" "$1"
}

status "🚀 Creating codespace for $REPO..."

# Create codespace and wait for it
gh codespace create \
  -R "$REPO" \
  -b "$BRANCH" \
  -m "$MACHINE" \
  --idle-timeout 5m \
  --retention-period 1h

# Wait a bit for creation to register
status "⏳ Waiting for codespace to register..."
sleep 5

# Get the newly created codespace (only Available ones)
status "🔍 Finding codespace..."
CODESPACE_NAME=$(gh codespace list | grep "$REPO" | grep "Available" | head -1 | awk '{print $1}')

if [ -z "$CODESPACE_NAME" ]; then
  printf "\r\033[K❌ Failed to get codespace name\n"
  printf "\033[?25h"  # Show cursor
  exit 1
fi

status "✅ Found codespace: $CODESPACE_NAME"

# Wait for codespace to be fully ready
status "⏳ Waiting for codespace to be ready..."
for i in {1..60}; do
  STATE=$(gh codespace view -c "$CODESPACE_NAME" 2>/dev/null | grep -i state | awk '{print $2}' || echo "Unknown")
  status "⏳ Waiting for codespace to be ready... ($STATE)"
  if [ "$STATE" = "Available" ]; then
    status "✅ Codespace is ready!"
    sleep 1
    break
  fi
  sleep 5
done

# Install Claude Code if API key is set
if [ -n "$ANTHROPIC_API_KEY" ]; then
  status "🔧 Installing Claude Code..."
  gh codespace ssh -c "$CODESPACE_NAME" -- bash -s <<'HEREDOC'
    set -e
    curl -fsSL https://claude.ai/install.sh | bash
HEREDOC
  
  # Set the API key in the codespace (export it in shell config files)
  status "🔑 Configuring API key..."
  gh codespace ssh -c "$CODESPACE_NAME" -- bash <<EOF
    echo 'export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"' >> ~/.bashrc
    echo 'export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"' >> ~/.profile
    echo 'export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"' >> ~/.bash_profile
    export ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
EOF
  
  # Verify the API key is set
  status "🔍 Verifying API key..."
  gh codespace ssh -c "$CODESPACE_NAME" -- bash -c "source ~/.bashrc && [ -n \"\$ANTHROPIC_API_KEY\" ] && echo 'API key verified' || echo 'API key not found'"
  
  status "✅ Setup complete!"
  sleep 1
else
  printf "\r\033[K❌ ANTHROPIC_API_KEY not set in .env\n"
  printf "\033[?25h"  # Show cursor
  exit 1
fi

# Start Claude with optional prompt
status "✨ Starting Claude Code..."
printf "\r\033[K"  # Clear status line
printf "\033[?25h"  # Show cursor

if [ -n "$PROMPT" ]; then
  gh codespace ssh -c "$CODESPACE_NAME" -- -t env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" bash -c "source ~/.bashrc && source ~/.profile && export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY' && cd /workspaces/* 2>/dev/null || cd ~ && claude -p '$PROMPT'"
else
  gh codespace ssh -c "$CODESPACE_NAME" -- -t env ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" bash -c "source ~/.bashrc && source ~/.profile && export ANTHROPIC_API_KEY='$ANTHROPIC_API_KEY' && cd /workspaces/* 2>/dev/null || cd ~ && exec claude"
fi

# After disconnecting, automatically delete the codespace
printf "\033[?25l"  # Hide cursor
status "🗑️  Deleting codespace..."
gh codespace delete -c "$CODESPACE_NAME" --force
printf "\r\033[K✅ Codespace deleted\n"
printf "\033[?25h"  # Show cursor
