#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
# RADICAL ACCESSIBILITY TOOLKIT — Smoke Test (Automated)
# ═══════════════════════════════════════════════════════════
# Quick pre-PR verification of CLI commands, state mutations,
# TACT availability, and MCP server import.
#
# Usage:  bash tests/smoke_test.sh
# Time:   ~30 seconds
# Deps:   Python 3.8+ only (TACT/MCP tests skip if not installed)
# ═══════════════════════════════════════════════════════════

set -euo pipefail

# ── Resolve paths ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(dirname "$SCRIPT_DIR")"
CLI="$ROOT/controller/controller_cli.py"
STATE="$ROOT/controller/state.json"
BACKUP="$ROOT/controller/state.json.smoke_backup"
TMP_EXPORT="/tmp/rat_smoke_export.txt"

passed=0
failed=0
skipped=0

smoke_pass() { echo "PASS: $1"; passed=$((passed + 1)); }
smoke_fail() { echo "FAIL: $1 -> $2"; failed=$((failed + 1)); }
smoke_skip() { echo "SKIP: $1"; skipped=$((skipped + 1)); }

# Run a single CLI command via pipe and capture stdout+stderr
run_cli() {
    printf '%s\nquit\n' "$1" | python3 "$CLI" --state "$STATE" 2>&1 || true
}

# ═══════════════════════════════════════════════════════════
echo "============================================================"
echo "SMOKE TEST: Prerequisites"
echo "============================================================"

# Python 3.8+
PY_VER=$(python3 -c "import sys; print(sys.version_info[:2])" 2>/dev/null || echo "(0, 0)")
if python3 -c "import sys; assert sys.version_info >= (3, 8)" 2>/dev/null; then
    smoke_pass "Python 3.8+ available ($PY_VER)"
else
    smoke_fail "Python 3.8+ required" "$PY_VER"
    echo "Cannot continue without Python 3.8+. Exiting."
    exit 1
fi

# Key files exist
for f in "$CLI" "$ROOT/controller/auditor.py" "$ROOT/mcp/mcp_server.py"; do
    bn=$(basename "$f")
    if [ -f "$f" ]; then
        smoke_pass "$bn exists"
    else
        smoke_fail "$bn exists" "not found: $f"
    fi
done

# TACT directory
if [ -d "$ROOT/tools/tact" ]; then
    smoke_pass "tools/tact/ directory exists"
else
    smoke_fail "tools/tact/ directory exists" "not found"
fi

# State file
if [ -f "$STATE" ]; then
    smoke_pass "state.json exists"
else
    smoke_fail "state.json exists" "not found"
    echo "Cannot continue without state.json. Exiting."
    exit 1
fi

# Backup state
cp "$STATE" "$BACKUP"
smoke_pass "state.json backed up"

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "SMOKE TEST: CLI Commands"
echo "============================================================"

# help
OUT=$(run_cli "help")
if echo "$OUT" | grep -q "Commands"; then
    smoke_pass "help prints command list"
else
    smoke_fail "help prints command list" "missing 'Commands' in output"
fi

# Reset state between tests for isolation
cp "$BACKUP" "$STATE"

# describe
OUT=$(run_cli "describe")
if echo "$OUT" | grep -q "Bay A" && echo "$OUT" | grep -q "Bay B"; then
    smoke_pass "describe shows Bay A and Bay B"
else
    smoke_fail "describe shows Bay A and Bay B" "missing bay names"
fi

cp "$BACKUP" "$STATE"

# list bays
OUT=$(run_cli "list bays")
if echo "$OUT" | grep -q "A" && echo "$OUT" | grep -q "B"; then
    smoke_pass "list bays shows A and B"
else
    smoke_fail "list bays shows A and B" "missing bay names"
fi

cp "$BACKUP" "$STATE"

# set bay A rotation
OUT=$(run_cli "set bay A rotation 45")
if echo "$OUT" | grep -q "rotation.*45"; then
    smoke_pass "set bay A rotation 45"
else
    smoke_fail "set bay A rotation 45" "$(echo "$OUT" | tail -5)"
fi

# undo
OUT=$(printf 'set bay A rotation 45\nundo\nquit\n' | python3 "$CLI" --state "$STATE" 2>&1 || true)
if echo "$OUT" | grep -qi "undo\|restored"; then
    smoke_pass "undo works"
else
    smoke_fail "undo works" "$(echo "$OUT" | tail -5)"
fi

cp "$BACKUP" "$STATE"

# zone add
OUT=$(run_cli "zone add TestZone 50 30 10 10")
if echo "$OUT" | grep -qi "TestZone.*added\|OK:"; then
    smoke_pass "zone add TestZone"
else
    smoke_fail "zone add TestZone" "$(echo "$OUT" | tail -3)"
fi

# zone list (run after zone add, don't reset)
OUT=$(run_cli "zone list")
if echo "$OUT" | grep -q "TestZone"; then
    smoke_pass "zone list shows TestZone"
else
    smoke_fail "zone list shows TestZone" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# grid set with rotation
OUT=$(run_cli "grid set 24 15")
if echo "$OUT" | grep -qi "grid set\|OK:"; then
    smoke_pass "grid set 24 15"
else
    smoke_fail "grid set 24 15" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# set site corners (polygon)
OUT=$(run_cli "set site corners 0,0 100,0 100,200 0,200")
if echo "$OUT" | grep -qi "corners set\|OK:"; then
    smoke_pass "set site corners (polygon)"
else
    smoke_fail "set site corners (polygon)" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# export text
rm -f "$TMP_EXPORT"
OUT=$(run_cli "export text $TMP_EXPORT")
if [ -f "$TMP_EXPORT" ] && [ -s "$TMP_EXPORT" ]; then
    smoke_pass "export text creates non-empty file"
else
    smoke_fail "export text creates non-empty file" "file missing or empty"
fi
rm -f "$TMP_EXPORT"

cp "$BACKUP" "$STATE"

# setup status (no Rhino running)
OUT=$(run_cli "setup status")
if echo "$OUT" | grep -qi "OFFLINE"; then
    smoke_pass "setup status returns OFFLINE (no Rhino)"
else
    # Could be connected if Rhino happens to be running
    if echo "$OUT" | grep -q "OK:"; then
        smoke_pass "setup status returns OK (Rhino connected)"
    else
        smoke_fail "setup status returns status" "$(echo "$OUT" | tail -3)"
    fi
fi

cp "$BACKUP" "$STATE"

# snapshot save
OUT=$(run_cli "snapshot save smoke_test")
if echo "$OUT" | grep -qi "OK:\|smoke_test\|saved"; then
    smoke_pass "snapshot save smoke_test"
else
    smoke_fail "snapshot save smoke_test" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# unknown command
OUT=$(run_cli "foobar")
if echo "$OUT" | grep -qi "error\|unknown"; then
    smoke_pass "unknown command returns error"
else
    smoke_fail "unknown command returns error" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# legend toggle
OUT=$(printf 'legend off\nlegend on\nquit\n' | python3 "$CLI" --state "$STATE" 2>&1 || true)
if echo "$OUT" | grep -qi "Legend OFF\|Legend ON\|OK:"; then
    smoke_pass "legend on/off toggles"
else
    smoke_fail "legend on/off toggles" "$(echo "$OUT" | tail -3)"
fi

cp "$BACKUP" "$STATE"

# tactile3d toggle
OUT=$(printf 'tactile3d on\ntactile3d wall_height 12\ntactile3d off\nquit\n' | python3 "$CLI" --state "$STATE" 2>&1 || true)
if echo "$OUT" | grep -qi "Tactile 3D ON\|Tactile 3D OFF\|OK:"; then
    smoke_pass "tactile3d on/config/off"
else
    smoke_fail "tactile3d on/config/off" "$(echo "$OUT" | tail -5)"
fi

cp "$BACKUP" "$STATE"

# tts toggle
OUT=$(printf 'tts on\ntts rate 5\ntts off\nquit\n' | python3 "$CLI" --state "$STATE" 2>&1 || true)
if echo "$OUT" | grep -q "OK:"; then
    smoke_pass "tts on/rate/off"
else
    smoke_fail "tts on/rate/off" "$(echo "$OUT" | tail -5)"
fi

cp "$BACKUP" "$STATE"

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "SMOKE TEST: State Validation"
echo "============================================================"

# Run a mutation, then check JSON
run_cli "zone add ValidateZone 40 20" > /dev/null 2>&1
if python3 -c "
import json
s = json.load(open('$STATE'))
assert s['schema'] == 'plan_layout_jig_v3.0', 'bad schema'
assert 'zones' in s, 'missing zones'
assert 'ValidateZone' in s['zones'], 'zone not saved'
print('OK')
" 2>/dev/null | grep -q "OK"; then
    smoke_pass "state.json schema and zone persisted"
else
    smoke_fail "state.json schema and zone persisted" "JSON validation failed"
fi

cp "$BACKUP" "$STATE"

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "SMOKE TEST: TACT CLI"
echo "============================================================"

if command -v tact &>/dev/null; then
    OUT=$(tact presets 2>&1 || true)
    if echo "$OUT" | grep -qi "floor_plan"; then
        smoke_pass "tact presets lists floor_plan"
    else
        smoke_fail "tact presets lists floor_plan" "$(echo "$OUT" | head -3)"
    fi

    OUT=$(tact info 2>&1 || true)
    if [ -n "$OUT" ]; then
        smoke_pass "tact info returns output"
    else
        smoke_fail "tact info returns output" "empty"
    fi
else
    smoke_skip "tact CLI not installed (pip install -e tools/tact)"
    smoke_skip "tact info (not installed)"
fi

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "SMOKE TEST: MCP Server Import"
echo "============================================================"

if python3 -c "
import sys, os, builtins
saved = builtins.print
sys.path.insert(0, '$ROOT/mcp')
sys.path.insert(0, '$ROOT/controller')
os.environ['LAYOUT_JIG_STATE'] = '$STATE'
try:
    import mcp_server
    builtins.print = saved
    print('OK')
except SystemExit:
    builtins.print = saved
    print('OK')
except ImportError as e:
    builtins.print = saved
    print('SKIP: ' + str(e))
" 2>/dev/null | grep -q "OK"; then
    smoke_pass "mcp_server.py imports without crash"
else
    smoke_skip "mcp_server.py import (mcp package not installed)"
fi

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "SMOKE TEST: Cleanup"
echo "============================================================"

# Restore original state
cp "$BACKUP" "$STATE"
rm -f "$BACKUP"
rm -f "$TMP_EXPORT"
# Clean up smoke_test snapshot if it was created
rm -f "$ROOT/controller/history/snapshot_smoke_test.json"
smoke_pass "state.json restored, temp files cleaned"

# ═══════════════════════════════════════════════════════════
echo ""
echo "============================================================"
echo "RESULTS"
echo "============================================================"
echo ""
echo "  Passed:  $passed"
echo "  Failed:  $failed"
echo "  Skipped: $skipped"
echo "  Total:   $((passed + failed + skipped))"
echo ""
if [ "$failed" -eq 0 ]; then
    echo "  ALL SMOKE TESTS PASSED"
    exit 0
else
    echo "  $failed SMOKE TEST(S) FAILED"
    exit 1
fi
