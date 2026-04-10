#!/bin/bash
# start-webui.sh — Start Claude Code with accessible web UI channel
# The channel server starts automatically as an MCP subprocess.
# Open http://localhost:8788 in your browser after launch.

cd /mnt/c/Users/ethan/Radical-Accessibility-Toolkit || exit 1

# Load NVM if needed
if ! command -v claude &>/dev/null; then
  export NVM_DIR="$HOME/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
fi

# Install deps if needed
if [ ! -d "tools/webui/node_modules" ]; then
  echo "Installing dependencies..."
  cd tools/webui && bun install && cd ../..
fi

echo "Starting Claude Code with accessible web UI..."
echo "Open http://localhost:8788 in your browser."
echo "Press Ctrl+C to stop."

claude --dangerously-load-development-channels server:webui
