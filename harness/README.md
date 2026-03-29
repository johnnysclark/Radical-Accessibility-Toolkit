# Rhino Automation Harness

Drive Rhino 3D through Claude Code. Connect to a running Rhino instance, execute IronPython scripts, query model state, and manage reusable scripts and session logs.

## Quick Start

```bash
pip install mcp
```

Add to `.mcp.json`:
```json
{
  "mcpServers": {
    "rhino-harness": {
      "command": "python3",
      "args": ["harness/mcp_server.py"]
    }
  }
}
```

In Rhino, run the watcher script to enable the TCP connection:
```
RunPythonScript tools/rhino/rhino_watcher.py
```

## Architecture

```
Claude Code  <-->  MCP Server (harness/mcp_server.py)
                        |
                   TCP :1998
                        |
                   Rhino Watcher (inside Rhino, IronPython 2.7)
                        |
                   Rhino Geometry
```

The MCP server sends JSON queries over TCP to the watcher process running inside Rhino. The watcher executes scripts in IronPython 2.7 and returns results.

## Tools

| Tool | Description |
|------|-------------|
| `rhino_status` | Connection check + basic stats |
| `rhino_connect` | Change host/port |
| `rhino_layers` | Layer names and object counts |
| `rhino_objects` | Object count (optionally by layer) |
| `rhino_bounds` | Bounding box of all geometry |
| `rhino_run` | Execute IronPython code in Rhino |
| `rhino_command` | Run a Rhino command string |
| `script_save` | Save a reusable script |
| `script_list` | List saved scripts |
| `script_show` | View script contents |
| `script_run` | Execute a saved script |
| `script_delete` | Remove a script |
| `session_log` | Log a session entry |
| `session_read` | Read recent log entries |
| `session_clear` | Clear the session log |
| `session_export` | Export full session log |

## Scripts

Saved scripts live in `harness/scripts/` as `.py` files with `.json` metadata sidecars. They must be IronPython 2.7 compatible (no f-strings, no pathlib).

## Hooks

Copy `harness/settings.example.json` into `.claude/settings.json` to enable:
- **PostToolUse**: Logs all harness MCP calls to `sessions/changes.jsonl`
- **Stop**: Writes session summary to `sessions/last-session.json`

## Web UI

The web UI at `tools/accessible-client/` provides a two-pane interface:
- **Terminal**: Send messages to Claude, see responses
- **Inspector**: Rhino status, layer stats, scripts, session log

Run with: `npx tsx tools/accessible-client/acclaude-channel.ts`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RHINO_HOST` | `127.0.0.1` | Rhino watcher host |
| `RHINO_PORT` | `1998` | Rhino watcher port |
