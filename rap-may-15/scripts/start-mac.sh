#!/bin/bash
set -e
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
echo "OK: Controller starting. To activate the Rhino watcher, in Rhino 8 Mac type:"
echo "    _-RunPythonScript \"$ROOT/rhino/startup.py\""
echo "Then run 'setup status' inside the controller to confirm the watcher is up."
exec python3 controller/console.py --state controller/state.json
