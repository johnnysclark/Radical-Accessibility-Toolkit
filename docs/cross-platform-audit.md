# Cross-Platform Audit Report

Date: 2026-03-18
Scope: Full RAP codebase audit for macOS (Rhino 8 Mac, CPython) compatibility.
Constraint: Windows workflow (Daniel, NVDA) must remain untouched.

## Summary

The RAP codebase is mostly cross-platform already. The controller (Python 3 stdlib),
MCP server, auditor, braille, skill manager, and style manager have zero platform
dependencies. The Rhino watcher has 3 isolated platform-specific locations. The
controller CLI has 2. Several student tools are Windows-only by design (screen
reader hooks, accessible client) and do not need porting.

Total files needing changes: 2 (rhino_watcher.py, controller_cli.py).
New files to create: 1 (compat.py).

---

## File-by-File Analysis

### tools/rhino/rhino_watcher.py

Runs inside Rhino. Currently IronPython 2.7 on Windows.

| Lines | Code | Category | Risk | Proposed Fix |
|-------|------|----------|------|-------------|
| 99-108 | `subprocess.Popen(["powershell", ... "[System.Console]::Beep(880, 120)"])` | Windows .NET via PowerShell | Low | Delegate to compat.chime(). Mac uses `afplay /System/Library/Sounds/Tink.aiff`. |
| 111-127 | `subprocess.Popen(["powershell", ... "System.Speech.Synthesis.SpeechSynthesizer"])` | Windows .NET via PowerShell | Low | Delegate to compat.speak(). Mac uses `say` command. |
| 1182 | `import System` | IronPython .NET import | Medium | Conditional: only on IronPython. CPython uses uuid module. |
| 1189 | `System.Guid(str(oid))` | IronPython .NET type | Medium | Use compat.make_guid(). Tries System.Guid first, falls back to uuid.UUID. |

Already cross-platform (no changes needed):
- Lines 34-40: try/except import of rhinoscriptsyntax, Rhino, scriptcontext (works on both).
- Lines 176-270: All geometry helpers use rhinoscriptsyntax (rs.*), fully cross-platform.
- Lines 1187-1206: Rhino.Geometry.Mesh/Brep/Extrusion — RhinoCommon API is identical on Mac.
- Lines 1513-1553: Rhino.RhinoApp.Idle event hook — same syntax on both platforms.
- Lines 1163-1170: os.stat() file polling — works identically on both.
- No f-strings used (IronPython 2.7 compatible). Uses .format() throughout.
- No pathlib used. Uses os.path throughout.

### controller/controller_cli.py

Runs in Python 3 on the host system (not inside Rhino).

| Lines | Code | Category | Risk | Proposed Fix |
|-------|------|----------|------|-------------|
| 81-106 | `_speak()` uses `subprocess.Popen(["powershell", ...])` | Windows PowerShell TTS | Low | Add platform detection. Mac uses `say` command. |
| 1793-1797 | `_RHINO_SEARCH_PATHS = [r"C:\Program Files\Rhino 8\...", ...]` | Hardcoded Windows paths | Low | Add Mac paths: `/Applications/Rhino 8.app/Contents/MacOS/Rhinoceros`. |
| 1829-1884 | `cmd_setup()` uses `/nosplash`, `/runscript=` Rhino flags | Windows Rhino CLI syntax | Medium | Add Mac launch: `open -a "Rhino 8"` or direct binary invocation. |
| 1861 | Error message contains `C:\\Program Files\\Rhino 8\\System\\Rhino.exe` | Hardcoded Windows path in error text | Low | Make conditional on platform. |

Already cross-platform (no changes needed):
- `_atomic_write()`: Uses os.replace(), works on all platforms.
- Command dispatch: Pure Python dict mapping, no platform dependencies.
- JSON state: Same schema everywhere.
- Undo stack: copy.deepcopy(), platform-agnostic.
- OK:/ERROR: output protocol: print() calls, fully portable.

### tools/rhino/tactile_print.py

Pure Python (stdlib only). No Rhino dependency. No platform-specific code.
Status: Already cross-platform. No changes needed.

### tools/rhino/rhino_client.py

TCP client using stdlib socket. Host/port via environment variables.
Status: Already cross-platform. No changes needed.

### controller/auditor.py

Pure Python math on JSON state. No imports beyond stdlib.
Status: Already cross-platform. No changes needed.

### controller/braille.py

Unicode Braille conversion. No platform dependencies.
Status: Already cross-platform. No changes needed.

### controller/skill_manager.py

JSON file operations via stdlib. Uses os.path for paths.
Status: Already cross-platform. No changes needed.

### controller/style_manager.py

JSON file operations via stdlib. Uses os.path for paths.
Status: Already cross-platform. No changes needed.

### mcp/mcp_server.py

Python 3, imports controller_cli and other controller modules.
Depends on `mcp` pip package. No platform-specific code.
Status: Already cross-platform. No changes needed.

### tools/tasc/src/tasc_core/rhino/commands.py

Line 115: Generates RhinoPython script strings containing `import System.Drawing as sd`.
This code is an embedded string executed inside Rhino, not in the controller.
On Rhino 8 Mac CPython, System.Drawing may need a conditional import.
Status: Safe for now. The generated script targets Rhino's internal Python.

### tools/tasc/src/tasc_core/rhino/connector.py

Lines 17-41: WSL2 detection via /proc/version. Uses `ip route` (Linux only).
On macOS: _is_wsl2() returns False (correct), gateway detection fails silently.
Falls back to RhinoCode CLI mode gracefully.
Status: Safe. No macOS breakage, but could add native Mac Rhino detection later.

### tools/screen-reader-hooks/ (announce.js, announce.ps1)

Entirely Windows-specific: PowerShell, JAWS DLLs, NVDA DLLs, WSL path conversion.
This is a Windows screen reader bridge by design.
Status: Windows-only, no port needed. macOS uses VoiceOver natively.

### tools/accessible-client/ (acclaude.ts, acclaude.bat)

acclaude.ts: Fully cross-platform Node.js. No platform-specific code.
acclaude.bat: Windows batch launcher. Could add acclaude.sh for Mac later.
Status: TypeScript is portable. Batch launcher is Windows-only but non-critical.

### tools/tact/src/tactile_core/utils/validators.py

Line 215: WSL detection via platform.uname().release. Correctly returns False on Mac.
Lines 219-223: Windows path conversion only runs in WSL context.
Status: Already cross-platform. No changes needed.

---

## Risk Assessment

### Trivial to port (low risk, additive changes only):
- Audio feedback (_chime, _speak) in rhino_watcher.py — add macOS subprocess calls
- Audio feedback (_speak) in controller_cli.py — add macOS subprocess calls
- Rhino search paths — add Mac paths to the list

### Moderate effort (medium risk, requires testing on Mac Rhino):
- System.Guid replacement in rhino_watcher.py — need to verify Rhino 8 Mac's .NET bridge
- cmd_setup() Rhino launch — Mac uses different command-line conventions
- TASC generated scripts with System.Drawing — may need conditional on Mac Rhino

### No port needed (Windows-only by design):
- Screen reader hooks (JAWS/NVDA are Windows-only)
- Accessible client batch launcher (macOS users use terminal directly)
- WSL2 detection code (correctly no-ops on Mac)

---

## Architecture Notes

The key insight is that RAP's architecture already enables cross-platform use:
1. Controller writes JSON (platform-agnostic).
2. Watcher reads JSON and draws geometry via rhinoscriptsyntax (cross-platform).
3. The only platform ties are audio feedback (PowerShell TTS) and Rhino launch helpers.

The compat.py approach wraps these in platform-conditional code without changing
any existing behavior on Windows.
