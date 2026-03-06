# Smoke Test Checklist -- Pre-PR Manual Verification

Branch: ethan/integrate-tools
Time: ~10 minutes
Prerequisite: Run `bash tests/smoke_test.sh` first (automated tests)

---

## A. CLI Interactive Session (2 min)

Open a terminal in the repo root.

- [ ] 1. `python3 controller/controller_cli.py`
  - Expect: "PLAN LAYOUT JIG v3.0" banner, "State:" path, prompt ">>"

- [ ] 2. Type `help`
  - Expect: Command list with "SITE & STYLE", "BAYS", "ZONES", "GRID"
  - Expect: No tables, no box-drawing characters

- [ ] 3. Type `describe`
  - Expect: Full model summary mentioning Bay A, Bay B, corridor, walls
  - Expect: Labeled lines, not dense paragraphs

- [ ] 4. Type `set bay A rotation 30`
  - Expect: Confirmation line with "rotation" and "30"

- [ ] 5. Type `undo`
  - Expect: "Undo." confirmation

- [ ] 6. Type `zone add Demo 40 20 10 10 residential`
  - Expect: Confirmation with zone name and area

- [ ] 7. Type `zone list`
  - Expect: Output includes "Demo" with area

- [ ] 8. Type `tts on` then `tts off`
  - Expect: Confirmation for each, no crash

- [ ] 9. Type `quit`
  - Expect: Clean exit, no traceback

---

## B. Rhino Integration (3 min)

Requires Rhino 7 or 8 installed on Windows.
WSL note: `setup rhino` now auto-detects WSL and launches Rhino via PowerShell bridge.

- [ ] 1. Start the CLI: `python3 controller/controller_cli.py`

- [ ] 2. Type `setup rhino`
  - Expect: Rhino launches on Windows side
  - Expect: "OK: Connected. Rhino is ready. Units: Feet."
  - Note: May take up to 30 seconds
  - If auto-detect fails: `setup rhino --path "C:\Program Files\Rhino 8\System\Rhino.exe"`

- [ ] 3. Type `set bay A spacing 30 30`
  - Expect: Confirmation in CLI
  - Expect: Rhino chime/audio within 1 second
  - Expect: "[PLJ] Rebuilt:" in Rhino command line

- [ ] 4. Check Rhino viewport
  - Expect: Columns visible on JIG_COLUMNS layer
  - Expect: Site boundary on JIG_SITE layer

- [ ] 5. Type `wall A on`
  - Expect: Wall geometry appears in Rhino

- [ ] 6. Type `wall A off`
  - Expect: Wall geometry removed

- [ ] 7. Type `setup status`
  - Expect: "OK: Rhino watcher is connected on 127.0.0.1:1998."

- [ ] 8. Close Rhino, then type `setup status`
  - Expect: "OFFLINE: Rhino watcher is not responding"

- [ ] 9. Type `quit`

---

## C. MCP Server (2 min)

Requires: `pip install mcp` and `.mcp.json` at repo root.
Run `python3 setup.py` to generate `.mcp.json` if missing.

- [ ] 1. Verify `.mcp.json` exists at repo root
  - Run: `cat .mcp.json`
  - Expect: "layout-jig" and "tactile" server entries with relative paths

- [ ] 2. In Claude Code, test `describe` MCP tool
  - Expect: Full model description returned

- [ ] 3. Test `run_command` with input `"zone list"`
  - Expect: Zone listing returned

- [ ] 4. Test `audit_model`
  - Expect: Audit report with bay analysis

- [ ] 5. Test `rhino_status`
  - Expect: "OFFLINE" or connection status

---

## D. TACT Tool (2 min)

Requires: `pip install -e tools/tact`

- [ ] 1. `tact presets`
  - Expect: Preset list including floor_plan, section, elevation

- [ ] 2. Test state render:
  `tact render controller/state.json`
  - Expect: PDF created at `controller/state_tactile.pdf`
  - Expect: File is non-empty

- [ ] 3. If test image available:
  `tact convert IMAGE.jpg --preset floor_plan --verbose`
  - Expect: Conversion output with progress info
  - Expect: PDF output file created

- [ ] 4. If MCP available, test `list_presets` MCP tool
  - Expect: Preset list returned

---

## E. JAWS Screen Reader (2 min)

Requires: JAWS running, cmd.exe (not Windows Terminal).

- [ ] 1. Open cmd.exe

- [ ] 2. Launch acclaude:
  `tools\accessible-client\acclaude.bat`
  - Expect: JAWS announces "Accessible Claude. Ready."

- [ ] 3. Type: "describe the current model"
  - Expect: Plain text response (no markdown, no emojis)
  - Expect: JAWS reads response clearly, no garbled characters

- [ ] 4. Type: "list the bays"
  - Expect: Bay listing in plain text
  - Expect: JAWS reads bay names

- [ ] 5. Type `/quit`
  - Expect: Clean exit

- [ ] 6. Fallback test: run `python controller_cli.py` in cmd.exe
  - Type `help`, `describe`, `set bay A rotation 10`
  - Expect: JAWS reads all output cleanly

---

## F. Output Format Spot-Check (1 min)

Can be done during any section above.

- [ ] 1. Mutation commands print a single confirmation line
- [ ] 2. No output contains ASCII art or box-drawing characters
- [ ] 3. No output contains wide tables or multi-column layouts
- [ ] 4. `describe` output uses short labeled lines
- [ ] 5. Error cases print "ERROR:" prefix (try: `set bay Z rotation 10`)
- [ ] 6. No output uses progress spinners or streaming indicators

---

## Results

Date: _______________
Tester: _______________

| Section | Result | Notes |
|---------|--------|-------|
| A. CLI Interactive | PASS / FAIL | |
| B. Rhino Integration | PASS / FAIL / SKIP | |
| C. MCP Server | PASS / FAIL / SKIP | |
| D. TACT Tool | PASS / FAIL / SKIP | |
| E. JAWS Screen Reader | PASS / FAIL / SKIP | |
| F. Output Format | PASS / FAIL | |

Overall: PASS / FAIL
