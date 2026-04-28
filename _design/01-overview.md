# 01 — Subsystem Overview

Four subsystems exist. Each is documented in its own file.

1. **CLI / Controller** (`_design/01-cli-controller.md`) — The command shell and state-mutation engine. Handles dispatch, undo, macros, styles, export, and all user-facing output. The largest single file (3135 LOC).

2. **MCP Server** (`_design/01-mcp-server.md`) — Bridges Claude Code (and other LLM agents) to the controller and Rhino. Exposes ~53 MCP functions. Acts as the agent-facing API layer over the CLI.

3. **Rhino Watcher + JSON Contracts** (`_design/01-rhino-watcher.md`) — File-watching loop (IronPython 2.7) that reads state.json and rebuilds Rhino geometry. Defines the data contract between the controller and the geometry renderer.

4. **Output Channels** (`_design/01-output-channels.md`) — TACT (tactile PDF/PIAF), TASC (site-planning CLI), Image Describer (alt-text), and Web UI (JAWS/NVDA client). These convert or render design state into physical or accessible formats.

Each subsystem file covers: purpose, public API / entry points, dependencies, what's essential, and what's accidental complexity.
