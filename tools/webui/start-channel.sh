#!/bin/bash
# webui MCP launcher.
#
# Boot-time port conflict was the #1 cause of "webui failed to connect":
# a leftover bun from a prior session held port 8788, the new bun crashed
# with EADDRINUSE, and Claude saw a dead stdio stream. Preflight kills
# any process on the port before launching.
#
# Override the port with WEBUI_PORT=NNNN if 8788 is being used by something
# you don't want killed.

set -u
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
cd "$(dirname "$0")"

PORT="${WEBUI_PORT:-8788}"
LOG=/tmp/webui-channel-err.log
TS() { date +%H:%M:%S; }

# Truncate the log so each session starts fresh and the user can read it.
: > "$LOG"
echo "[webui $(TS)] launcher starting; PORT=$PORT cwd=$(pwd)" >> "$LOG"

# Preflight: kill anything bound to the chosen port.
EXISTING="$(lsof -ti:"$PORT" 2>/dev/null || true)"
if [ -n "$EXISTING" ]; then
  echo "[webui $(TS)] killing stale pid(s) on $PORT: $EXISTING" >> "$LOG"
  # shellcheck disable=SC2086
  kill -9 $EXISTING 2>/dev/null || true
  # Brief pause so the kernel actually releases the socket.
  sleep 0.3
fi

# Sanity-check that bun is on PATH; without it the exec would silently fail.
if ! command -v bun >/dev/null 2>&1; then
  echo "[webui $(TS)] FATAL: 'bun' not found on PATH ($PATH)" >> "$LOG"
  exit 127
fi

echo "[webui $(TS)] starting bun run channel-server.ts" >> "$LOG"
exec env WEBUI_PORT="$PORT" bun run channel-server.ts 2>>"$LOG"
