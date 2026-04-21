#!/bin/bash
# rhino-doctor.sh — diagnose Rhino MCP port connectivity from WSL.
#
# Non-admin, read-only by default. When admin action is needed (deleting
# portproxy rules, removing duplicate firewall rules), prints the exact
# PowerShell line for the user to paste — never improvises.
#
# Output is screen-reader-friendly: every line starts with a labelled
# prefix (OK:, WARN:, ERROR:, INFO:, HINT:). No tables, no box-drawing.
# Ends with a READY: line.
#
# Exit codes:
#   0 — all checks pass
#   1 — user action needed (zombie process, stale rules, etc.)
#   2 — can't reach Windows from WSL (broken interop)
#   3 — Rhino not running on Windows
#
# Usage: bash tools/rhino/rhino-doctor.sh

set -u

# ── Path discovery (no hardcoded usernames) ───────────────────────────
# cmd.exe chdir warning on /mnt paths goes to stderr; suppress it.
WIN_USER="$(cmd.exe /c 'echo %USERNAME%' 2>/dev/null | tr -d '\r\n ')"
if [ -z "$WIN_USER" ]; then
  echo "ERROR: cannot read Windows username — cmd.exe interop is broken."
  echo "HINT:  try 'wsl --shutdown' from Windows PowerShell, then reopen."
  echo "READY:"
  exit 2
fi
WIN_HOME="/mnt/c/Users/$WIN_USER"
WSLCONFIG="$WIN_HOME/.wslconfig"

LAUNCHER_LOG="/tmp/rhinomcp-err.log"
RHINO_PORT=1999
WATCHER_PORT=1998

ACTION_NEEDED=0
RHINO_RUNNING=0

# Helper: probe a TCP endpoint with a 1s timeout. Returns 0 on connect.
probe() {
  local host="$1" port="$2"
  timeout 1 bash -c "exec 3<>/dev/tcp/$host/$port" 2>/dev/null
}

# Helper: look up the Windows process name for a PID.
# Returns "name.exe" or "unknown" on failure.
proc_name_for_pid() {
  local pid="$1"
  local name
  name="$(tasklist.exe /FI "PID eq $pid" /FO CSV /NH 2>/dev/null \
          | tr -d '\r' | head -1 | awk -F'","' '{print $1}' | tr -d '"')"
  if [ -z "$name" ] || [ "$name" = "INFO: No tasks are running which match the specified criteria." ]; then
    echo "unknown"
  else
    echo "$name"
  fi
}

# Helper: find the PID(s) bound to a local port via netstat.exe.
# Prints one PID per line, or nothing if unbound. LISTENING state only.
# Only sees WINDOWS-side processes. WSL-side holders are invisible here.
pids_on_port_windows() {
  local port="$1"
  netstat.exe -ano 2>/dev/null | tr -d '\r' \
    | awk -v p=":$port" '$2 ~ p"$" && $4 == "LISTENING" {print $5}' \
    | sort -u
}

# Helper: find the WSL-side process holding a local port (ss output).
# Under mirrored networking a WSL bind on 127.0.0.1 still blocks Rhino.
# Prints "name:pid" per hit, or nothing.
wsl_holders_on_port() {
  local port="$1"
  ss -tlnp 2>/dev/null \
    | awk -v p=":$port" '$4 ~ p"$" {print $NF}' \
    | sed -n 's/.*users:(("\([^"]*\)",pid=\([0-9]*\).*/\1:\2/p'
}

echo "INFO: running rhino-doctor from WSL as $USER (Windows user: $WIN_USER)"
echo ""

# ── Check 1: mirrored networking ──────────────────────────────────────
if [ ! -f "$WSLCONFIG" ]; then
  echo "WARN: no .wslconfig at $WSLCONFIG"
  echo "HINT: mirrored networking is the supported mode. Create the file with [wsl2] and networkingMode=mirrored, then 'wsl --shutdown' from admin PowerShell."
  ACTION_NEEDED=1
elif grep -q '^networkingMode=mirrored' "$WSLCONFIG" 2>/dev/null; then
  echo "OK:   mirrored networking enabled in $WSLCONFIG"
else
  echo "WARN: .wslconfig exists but networkingMode=mirrored is missing"
  echo "HINT: add the line under [wsl2], then 'wsl --shutdown' from admin PowerShell."
  ACTION_NEEDED=1
fi

# ── Check 2: Rhino process ────────────────────────────────────────────
RHINO_PIDS="$(tasklist.exe /FI "IMAGENAME eq Rhino.exe" /FO CSV /NH 2>/dev/null \
              | tr -d '\r' | awk -F'","' '/^"Rhino.exe"/ {print $2}' | tr -d '"')"
if [ -z "$RHINO_PIDS" ]; then
  echo "ERROR: Rhino is not running on Windows"
  echo "HINT:  double-click tools/rhino/start-rhino.bat, wait for '[STARTUP] Ready'"
else
  RHINO_RUNNING=1
  RHINO_PID_COUNT="$(echo "$RHINO_PIDS" | wc -l | tr -d ' ')"
  if [ "$RHINO_PID_COUNT" -gt 1 ]; then
    echo "WARN: multiple Rhino.exe processes running: $(echo "$RHINO_PIDS" | tr '\n' ' ')"
    echo "HINT: close extras; only one should hold port $RHINO_PORT"
    ACTION_NEEDED=1
  else
    echo "OK:   Rhino.exe running (PID $RHINO_PIDS)"
  fi
fi

# Helper: run both-side port checks and report. Usage: check_port <port> <role>
# role is "rhino" (plugin) or "watcher" — controls the wording.
check_port() {
  local port="$1" role="$2"
  local win_pids wsl_hits bound_by_rhino=0 blocker=0
  win_pids="$(pids_on_port_windows "$port")"
  wsl_hits="$(wsl_holders_on_port "$port")"

  if [ -n "$win_pids" ]; then
    for pid in $win_pids; do
      local name
      name="$(proc_name_for_pid "$pid")"
      if [ "$name" = "Rhino.exe" ]; then
        echo "OK:   port $port bound by Rhino.exe (PID $pid)"
        bound_by_rhino=1
      else
        echo "ERROR: port $port bound by $name (PID $pid) on Windows — not Rhino"
        echo "HINT:  from WSL, run: taskkill.exe /PID $pid /F   (no admin needed for own-user)"
        blocker=1
      fi
    done
  fi

  if [ -n "$wsl_hits" ]; then
    # Use process substitution, not pipe — keeps the loop in this shell
    # so `blocker=1` below still propagates.
    while IFS=: read -r name pid; do
      echo "ERROR: port $port bound by WSL-side $name (PID $pid) — will block Rhino's _mcpstart under mirrored mode"
      echo "HINT:  from WSL, run: kill $pid"
    done < <(echo "$wsl_hits")
    blocker=1
  fi

  if [ "$bound_by_rhino" -eq 0 ] && [ "$blocker" -eq 0 ]; then
    if [ "$RHINO_RUNNING" -eq 1 ]; then
      if [ "$role" = "rhino" ]; then
        echo "ERROR: port $port is not bound — _mcpstart never succeeded inside Rhino"
        echo "HINT:  in Rhino's command line, type: _mcpstart"
      else
        echo "WARN: port $port is not bound — watcher not running"
        echo "HINT: startup.py may not have completed; check Rhino command line for [STARTUP] Ready"
      fi
      blocker=1
    else
      echo "INFO: port $port is unbound (expected — Rhino not running)"
    fi
  fi

  if [ "$blocker" -eq 1 ]; then
    ACTION_NEEDED=1
  fi
}

# ── Check 3: port 1999 (RhinoMCP plugin) ──────────────────────────────
check_port "$RHINO_PORT" "rhino"

# ── Check 4: port 1998 (watcher) ──────────────────────────────────────
check_port "$WATCHER_PORT" "watcher"

# ── Check 5: WSL→Windows TCP probes ───────────────────────────────────
# Under mirrored mode 127.0.0.1 works directly. Fall back to gateway
# so we can diagnose non-mirrored setups too.
GATEWAY="$(ip route show default 2>/dev/null | awk 'NR==1 {print $3}')"
for port in $RHINO_PORT $WATCHER_PORT; do
  reached=""
  for host in "127.0.0.1" "$GATEWAY"; do
    [ -z "$host" ] && continue
    if probe "$host" "$port"; then
      reached="$host"
      break
    fi
  done
  if [ -n "$reached" ]; then
    echo "OK:   WSL can reach port $port via $reached"
  else
    if [ "$RHINO_RUNNING" -eq 1 ]; then
      echo "ERROR: WSL cannot reach port $port on the Windows host"
      echo "HINT:  port shows bound above but WSL can't connect — likely Windows Firewall or mirrored mode disabled"
      ACTION_NEEDED=1
    else
      echo "INFO: WSL probe of port $port failed (expected — Rhino not running)"
    fi
  fi
done

# ── Check 6: stale portproxy rules ────────────────────────────────────
PROXY_RULES="$(netsh.exe interface portproxy show v4tov4 2>/dev/null | tr -d '\r' \
               | awk '/[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/ && ($2 == 1998 || $2 == 1999) {print}')"
if [ -z "$PROXY_RULES" ]; then
  echo "OK:   no stale portproxy rules for $WATCHER_PORT/$RHINO_PORT"
else
  echo "WARN: stale portproxy rules present (redundant under mirrored networking):"
  echo "$PROXY_RULES" | while IFS= read -r line; do
    listen_addr="$(echo "$line" | awk '{print $1}')"
    listen_port="$(echo "$line" | awk '{print $2}')"
    echo "INFO:   rule: listen $listen_addr:$listen_port"
    echo "HINT:   in admin PowerShell: netsh interface portproxy delete v4tov4 listenport=$listen_port listenaddress=$listen_addr"
  done
  ACTION_NEEDED=1
fi

# ── Check 7: firewall rules for 1998/1999 ─────────────────────────────
FIREWALL_HITS="$(netsh.exe advfirewall firewall show rule name=all 2>/dev/null | tr -d '\r' \
                 | awk '
                     /^Rule Name:/ { name=$0; sub(/^Rule Name: */,"",name); next }
                     /LocalPort:.*(1998|1999)/ { print name }
                   ')"
if [ -z "$FIREWALL_HITS" ]; then
  echo "INFO: no firewall rules touch ports $WATCHER_PORT/$RHINO_PORT"
  echo "HINT: under mirrored networking none are needed. If WSL probes above failed, this may be why."
else
  RULE_COUNT="$(echo "$FIREWALL_HITS" | wc -l | tr -d ' ')"
  UNIQUE_NAMES="$(echo "$FIREWALL_HITS" | sort | uniq -c | awk '{c=$1; $1=""; sub(/^ +/,""); print c" x "$0}')"
  if [ "$RULE_COUNT" -gt 1 ]; then
    echo "WARN: $RULE_COUNT firewall rules touch ports $WATCHER_PORT/$RHINO_PORT (duplicates accumulate over time):"
    echo "$UNIQUE_NAMES" | while IFS= read -r n; do
      echo "INFO:   rule: $n"
    done
    echo "HINT: list them in admin PowerShell: Get-NetFirewallPortFilter | Where-Object { \$_.LocalPort -match '199[89]' } | ForEach-Object { (Get-NetFirewallRule -AssociatedNetFirewallPortFilter \$_).DisplayName }"
    echo "HINT: remove by name (removes ALL with that name): Remove-NetFirewallRule -DisplayName '<NAME>'"
    ACTION_NEEDED=1
  else
    echo "OK:   one firewall rule touches ports $WATCHER_PORT/$RHINO_PORT: $FIREWALL_HITS"
  fi
fi

# ── Check 8: recent launcher log ──────────────────────────────────────
if [ -f "$LAUNCHER_LOG" ] && [ -s "$LAUNCHER_LOG" ]; then
  echo "INFO: last 10 lines of $LAUNCHER_LOG:"
  tail -n 10 "$LAUNCHER_LOG" | while IFS= read -r line; do
    echo "INFO:   $line"
  done
else
  echo "INFO: launcher log $LAUNCHER_LOG is empty or missing (no recent Claude session used rhinomcp)"
fi

echo ""
if [ "$ACTION_NEEDED" -ne 0 ]; then
  echo "READY: exit 1 — user action needed (see HINT lines above)"
  exit 1
elif [ "$RHINO_RUNNING" -eq 0 ]; then
  echo "READY: exit 3 — Rhino not running"
  exit 3
else
  echo "READY: exit 0 — all checks pass"
  exit 0
fi
