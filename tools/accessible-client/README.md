# acclaude -- Accessible Claude Code Client

A JAWS/NVDA-compatible wrapper around Claude Code that bypasses the Ink TUI entirely. Designed for blind and low-vision users who need plain text output and screen reader announcements.

## How It Works

Uses `claude -p` (headless/print mode) with `--resume SESSION_ID` for multi-turn conversations. All markdown, ANSI codes, and emojis are stripped before output.

## Requirements

- Node.js 18+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- JAWS or NVDA (optional, for TTS announcements)

## Usage

From WSL2 or Linux:
```
./acclaude
```

From Windows:
```
acclaude.bat
```

## Slash Commands

- /help -- show available commands
- /repeat -- repeat last response
- /history -- show conversation history
- /new -- start new conversation
- /quit -- exit

## Session Memory

Session history persists at ~/.radical-accessibility/memory/ across restarts.

## Modules

- acclaude.ts -- main entry point
- text-cleaner.ts -- strips markdown, ANSI, emojis
- announce-bridge.ts -- WSL2-to-PowerShell bridge for JAWS TTS
- memory-store.ts -- session persistence
