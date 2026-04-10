# Web UI -- Accessible Claude Code Interface

An accessible web UI for Claude Code that bypasses the Ink TUI entirely. Designed for blind and low-vision users who need plain text output and screen reader compatibility.

## How It Works

Runs as an MCP channel server under Claude Code. Serves a web UI at `http://localhost:8788` with three panes: Chat, Model Navigator, and Script Editor. All markdown, ANSI codes, and emojis are stripped before output.

## Requirements

- Node.js 18+
- bun (runtime for the channel server)
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- JAWS or NVDA (optional, for TTS announcements)

## Usage

From Windows:
```
start-webui.bat
```

From WSL2 or Linux:
```
bash start-webui.sh
```

## Modules

- channel-server.ts -- MCP channel server, HTTP endpoints, SSE events
- text-cleaner.ts -- strips markdown, ANSI, emojis
- index.html -- web UI frontend
- start-channel.sh -- channel server launcher
- start-webui.sh -- main entry point (starts Claude Code with channel)
- start-webui.bat -- Windows launcher
- hooks/ -- screen reader lifecycle hooks
