# Accessible Claude Code Clients

Two interfaces for blind and low-vision users to interact with Claude Code and Rhino models. Both strip markdown, ANSI codes, and emojis before output.

## Accessible Web UI (acclaude-channel)

A two-pane browser interface served on localhost:8788 via a Claude Code Channel server.

- Chat pane: send messages to Claude, receive replies via Server-Sent Events
- Model Navigator pane: query Rhino objects via RhinoMCP, edit position (X/Y/Z), apply changes
- Dark theme with WCAG AAA contrast ratios (13:1)
- ARIA landmarks (banner, main, complementary, status)
- Keyboard shortcuts: Alt+1 (chat), Alt+2 (navigator), Alt+R (refresh inventory)
- Permission prompts displayed inline with Allow/Deny buttons

### Requirements

- Bun runtime
- Claude Code CLI
- RhinoMCP plugin installed in Rhino (for Model Navigator)

### Usage

```
cd Radical-Accessibility-Toolkit
bun install --cwd tools/accessible-client
claude --dangerously-load-development-channels server:acclaude-channel
```

Open http://localhost:8788 in your browser.

Or use the launch script:

```
./tools/accessible-client/start-acclaude.sh
```

### Architecture

```
Browser (localhost:8788)
  |-- SSE stream (GET /events) -- real-time replies from Claude
  |-- POST /chat -- send chat messages
  |-- POST /edit -- send object position edits
  |-- POST /permission -- respond to tool permission prompts
  |
acclaude-channel.ts (MCP channel server)
  |-- MCP stdio transport to Claude Code
  |-- reply tool -- sends chat text to browser via SSE
  |-- inventory_reply tool -- sends Rhino object data to Model Navigator
  |
Claude Code
  |-- rhinomcp get_document_info -- query Rhino objects
  |-- rhinomcp modify_object -- apply edits
```

---

## Terminal Client (acclaude)

A JAWS/NVDA-compatible terminal wrapper around Claude Code that bypasses the Ink TUI entirely. Designed for users who prefer a terminal REPL.

### How It Works

Uses `claude -p` (headless/print mode) with `--resume SESSION_ID` for multi-turn conversations. All markdown, ANSI codes, and emojis are stripped before output.

### Requirements

- Node.js 18+
- Claude Code CLI installed (`npm install -g @anthropic-ai/claude-code`)
- JAWS or NVDA (optional, for TTS announcements)

### Usage

From WSL2 or Linux:
```
./acclaude
```

From Windows:
```
acclaude.bat
```

### Slash Commands

- /help -- show available commands
- /repeat -- repeat last response
- /history -- show conversation history
- /new -- start new conversation
- /quit -- exit

### Session Memory

Session history persists at ~/.radical-accessibility/memory/ across restarts.

---

## Shared Modules

- text-cleaner.ts -- strips markdown, ANSI, emojis, HTML
- announce-bridge.ts -- WSL2-to-PowerShell bridge for JAWS/NVDA TTS
- memory-store.ts -- session persistence (terminal client)
- package.json -- dependencies (@modelcontextprotocol/sdk, zod)
