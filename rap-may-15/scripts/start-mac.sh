#!/bin/bash
set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
WATCHER_CMD="_-RunPythonScript \"$ROOT/rhino/startup.py\""

echo "OK: Controller starting."
echo "To activate the Rhino watcher, in Rhino 8 Mac type at the command line:"
echo "    $WATCHER_CMD"

# Pre-populate macOS clipboard so the user can Cmd-V in Rhino
if command -v pbcopy >/dev/null 2>&1; then
    printf "%s" "$WATCHER_CMD" | pbcopy
    echo "OK: Watcher command copied to clipboard. In Rhino, press Cmd-V then Return."
fi

echo "After the watcher is active, type 'setup status' inside the controller to confirm."
echo "READY:"
exec python3 controller/console.py --state controller/state.json
