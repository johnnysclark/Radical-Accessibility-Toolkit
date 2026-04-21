#!/bin/bash
# rhinomcp MCP launcher.
#
# `rhinomcp` is the external bridge — it speaks MCP stdio to Claude and
# forwards calls over TCP to the RhinoMCP plugin running INSIDE Rhino
# (started by tools/rhino/startup.py via `_mcpstart`). If Rhino isn't
# reachable, the bridge hangs trying to connect and Claude times out the
# handshake.
#
# WSL gateway IP CHANGES every Windows reboot, so we auto-discover it
# instead of hardcoding 172.28.208.1. Candidates are tried in this order:
#   1. RHINO_MCP_HOST env var (if set and not "auto")
#   2. WSL2 default gateway (`ip route show default`) — usually right
#   3. 127.0.0.1 — works when WSL2 localhostForwarding is enabled
# The first host that answers a TCP connect on RHINO_MCP_PORT (default
# 1999) wins, and that value is exported to the rhinomcp process.

set -u
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"

LOG=/tmp/rhinomcp-err.log
TS() { date +%H:%M:%S; }

: > "$LOG"

RHINO_MCP_PORT="${RHINO_MCP_PORT:-1999}"
USER_HOST="${RHINO_MCP_HOST:-auto}"

CANDIDATES=()
if [ "$USER_HOST" != "auto" ] && [ -n "$USER_HOST" ]; then
  CANDIDATES+=("$USER_HOST")
fi
GATEWAY="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"
if [ -n "$GATEWAY" ]; then
  CANDIDATES+=("$GATEWAY")
fi
CANDIDATES+=("127.0.0.1")

echo "[rhinomcp $(TS)] launcher starting; port=$RHINO_MCP_PORT" >> "$LOG"
echo "[rhinomcp $(TS)] candidates (in order): ${CANDIDATES[*]}" >> "$LOG"

if ! command -v uvx >/dev/null 2>&1; then
  echo "[rhinomcp $(TS)] FATAL: 'uvx' not found on PATH. Install uv: https://docs.astral.sh/uv/" >> "$LOG"
  exit 127
fi

# Probe each candidate with a 1-second TCP connect; first to answer wins.
SELECTED=""
for HOST in "${CANDIDATES[@]}"; do
  if timeout 1 bash -c "exec 3<>/dev/tcp/$HOST/$RHINO_MCP_PORT" 2>/dev/null; then
    SELECTED="$HOST"
    echo "[rhinomcp $(TS)] reachable: $HOST:$RHINO_MCP_PORT — using this" >> "$LOG"
    break
  fi
  echo "[rhinomcp $(TS)] unreachable: $HOST:$RHINO_MCP_PORT" >> "$LOG"
done

if [ -z "$SELECTED" ]; then
  echo "[rhinomcp $(TS)] FATAL: no candidate host answered on port $RHINO_MCP_PORT." >> "$LOG"
  echo "[rhinomcp $(TS)]        1. Is Rhino running, and did startup.py print '[STARTUP] Ready'?" >> "$LOG"
  echo "[rhinomcp $(TS)]        2. Is the firewall blocking inbound TCP $RHINO_MCP_PORT on the Windows host?" >> "$LOG"
  echo "[rhinomcp $(TS)]        3. To force a host, run: RHINO_MCP_HOST=NNN.NNN.NNN.NNN claude ..." >> "$LOG"
  exit 1
fi

export RHINO_MCP_HOST="$SELECTED"
echo "[rhinomcp $(TS)] launching uvx rhinomcp (RHINO_MCP_HOST=$SELECTED)" >> "$LOG"
exec uvx rhinomcp 2>>"$LOG"
