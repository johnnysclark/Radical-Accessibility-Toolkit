# rhino-driver — Manual & Test-Drive Guide

A complete walkthrough of the cross-platform driver that pushes a **TASC** model
into **Rhino** — what it does, exactly how it works internally, and a hands-on
test drive you can follow with or without Rhino installed.

> **Taxonomy note.** In RAP terms this is a **Tool** (a major capability module).
> Its individual actions (`status`, `draw`, `render`, `clear`) are **Commands**.
> It is not a macro, skill, or template.

---

## Table of contents

1. [What problem this solves](#1-what-problem-this-solves)
2. [The one-paragraph fix](#2-the-one-paragraph-fix)
3. [How it works in detail](#3-how-it-works-in-detail)
4. [Install](#4-install)
5. [Test drive A — no Rhino required (works anywhere)](#5-test-drive-a--no-rhino-required-works-anywhere)
6. [Test drive B — macOS with Rhino 8 (the headline path)](#6-test-drive-b--macos-with-rhino-8-the-headline-path)
7. [Test drive C — Windows / WSL2 over the RhinoMCP socket](#7-test-drive-c--windows--wsl2-over-the-rhinomcp-socket)
8. [Command reference](#8-command-reference)
9. [Environment variables & exit codes](#9-environment-variables--exit-codes)
10. [Troubleshooting](#10-troubleshooting)
11. [How it fits the rest of RAP](#11-how-it-fits-the-rest-of-rap)
12. [Running and reading the test suite](#12-running-and-reading-the-test-suite)

---

## 1. What problem this solves

RAP drives Rhino three ways: the interactive controller CLI → `state.json` →
Rhino **watcher** (IronPython, Windows-only), the MCP server (Claude) over the
same path, and **TASC** — the only *cross-platform* driver, which talks to Rhino
directly. TASC tries, in order: a **RhinoMCP socket**, the **`rhinocode` CLI**,
then **offline**. The `rhinocode` route is the macOS path — and it never worked.
Two independent bugs, plus a silent-failure habit, meant that on a Mac, TASC
created eight empty layers and **zero geometry**, while reporting success.

**Bug 1 — the CLI invocation was fictional.** The old code ran
`rhinocode exec --code "<inline code>"`. That subcommand and flag do not exist.
Rhino 8's real CLI is `rhinocode [--rhino <instance>] script <file.py>` (Rhino ≥
8.11), and it requires the in-Rhino **`StartScriptServer`** to be running first.
A real Rhino errored; the old code caught the error and wrapped it as
`{"status": "ok"}` — false success.

**Bug 2 — the command translation read the wrong shape.** The old translator
read `params["object_type"]` / `params["points"]`, but the protocol emits
`params["type"]` (e.g. `"POLYLINE"`) with geometry nested under
`params["params"]`. Every `create_object` fell through to a no-op
`# Unsupported command` comment. Circles, text/labels, layer selection, deletes,
and raw scripts weren't translated at all.

**Habit — silent failure.** Draw calls were wrapped in `try/except: pass`, which
violates the project's own rule: *"Silence after a command means something broke."*

`rhino-driver` is a clean, standalone tool that fixes all three and supersedes
that path. It does **not** modify the existing `tools/tasc/src/tasc/rhino/`
files; it reuses them by import.

---

## 2. The one-paragraph fix

Instead of pushing one socket command per object (slow over the socket, and on
macOS broken), `rhino-driver` collects the **entire model** into one ordered list
of protocol commands and translates that into **one deterministic RhinoPython
script** — a full rebuild that clears prior TASC geometry and redraws everything.
The same script runs over whichever transport is live: as a single
`execute_rhinoscript_python_code` over the RhinoMCP socket, or via
`rhinocode script <file>` on macOS. If neither is available the driver is
**offline** and says so, with the exact next step. This mirrors the watcher's
blessed *"same state → one deterministic full rebuild"* model.

---

## 3. How it works in detail

### 3.1 Components

| File | Responsibility |
|------|----------------|
| `render.py` | Model → one RhinoPython script. Holds the **command→script translator** and the `CollectingConnector` that reuses TASC geometry. |
| `rhinocode.py` | The real `rhinocode` CLI wrapper: locate the binary, discover live instances, run a script file once. |
| `driver.py` | `RhinoDriver`: choose a transport, send the one script, and report status honestly. |
| `cli.py` | The accessible `rhino-driver` CLI (`status`/`doctor`, `draw`, `clear`, `render`). |

### 3.2 Data flow

```
.tasc_state.json
      │  TASCModel.load
      ▼
  TASCModel ──────────────► model_to_commands(model)
                                 │  drives tasc.rhino.commands.RhinoDrawer.redraw
                                 │  against a CollectingConnector (records, never sends)
                                 ▼
                       list[ protocol command dict ]   ← clear + layers + ALL geometry
                                 │  commands_to_script
                                 ▼
                       one RhinoPython script (str)
                                 │  RhinoDriver.run_script
              ┌──────────────────┼─────────────────────┐
              ▼                   ▼                     ▼
      mcp socket:           rhinocode:              offline:
   ONE execute_            temp .py +              structured
   rhinoscript_           `rhinocode               "nothing drawn"
   python_code             script <file>`           status
```

### 3.3 Why a `CollectingConnector` (no geometry duplication)

The bay/grid/column/corridor/void math is non-trivial and already lives in
`tasc.rhino.commands.RhinoDrawer`. Rewriting it here would create a second source
of truth that drifts. Instead we hand the *real* drawer a stand-in connector that
implements exactly the surface it touches — `is_live` and `send` — and records
each protocol command instead of transmitting it:

```python
class CollectingConnector:
    is_live = True
    def __init__(self): self.commands = []
    def send(self, command_type, params):
        self.commands.append({"type": command_type, "params": params})
        return {"status": "ok", "output": ""}
```

`RhinoDrawer.redraw(model)` then produces the full, correctly-ordered command
stream (clear → layers → display mode → site → grid → bays/columns/corridors/voids
→ zones), and we translate that. The geometry stays single-sourced in TASC.

### 3.4 The translator (`commands_to_script`)

It reads the protocol's **real** shapes and emits documented `rs.*` calls:

| Protocol command | RhinoPython emitted |
|------------------|---------------------|
| `get_or_set_current_layer` | `rs.IsLayer/AddLayer` + `rs.CurrentLayer(name)` |
| `create_layer` | guarded `rs.AddLayer(name, [r,g,b])` |
| `create_object` POLYLINE | `rs.AddPolyline([...])` + `rs.ObjectName` + `rs.ObjectColor` |
| `create_object` LINE | `rs.AddLine(start, end)` + color |
| `create_object` CIRCLE | `rs.AddCircle(center, radius)` + color |
| `create_object` POINT (named) | `rs.AddTextDot(text, pt)` — a *visible* label for the tactile capture |
| `delete_object` | all / by name (`rs.ObjectsByName`) / by id |
| `execute_rhinoscript_python_code` | inlined verbatim (redundant `import rhinoscriptsyntax` lines de-duplicated) |

**Injection-proof strings.** Every name/label is embedded with
`json.dumps(str(value), ensure_ascii=True)`. That double-quotes and escapes
quotes, backslashes, newlines, and non-ASCII (Braille → `\uXXXX`). A zone named
`O'Brien "Wing"` or `⠇⠊⠃` can never break the generated source — and because the
output is ASCII-only it needs no source-encoding line and runs under **both**
CPython 3 and IronPython 2.7 (Rhino can use either).

### 3.5 The real `rhinocode` path (`rhinocode.py`)

- **Locate the binary:** `PATH` first, then the macOS bundle
  `/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode`.
- **Discover instances:** `rhinocode list`, parsing ids like
  `rhinocode_remotepipe_75029`. An empty list means *no live script server*.
- **Run once:** write the script to a temp `.py` (UTF-8) and execute
  `rhinocode --rhino <id> script <tempfile>`; capture stdout+stderr; a non-zero
  return code becomes `status: "error"` (never a fake "ok"). Timeout is
  configurable via `TASC_RHINO_TIMEOUT` (default 60s).

### 3.6 Transport selection & honesty (`driver.py`)

`connect()` tries the MCP socket, then (in WSL2) the auto-detected Windows
gateway IP, then `rhinocode` **only if a live instance exists**, then offline. It
never selects a transport that would silently do nothing. `status()` probes every
transport independently and returns a labeled diagnosis plus the single most
useful next action — which is how the CLI turns failure into guidance instead of
silence.

### 3.7 Tie-back to RAP principles

- **Determinism / crash-only:** one full-rebuild script; same model → same
  geometry; the model lives in JSON, not Rhino's memory.
- **Accessibility-first IO:** short labeled lines, `OK:`/`ERROR:` prefixes,
  `READY:` terminator, no spinners, never silent.
- **Controller/viewer separation:** the model is authoritative; Rhino is a
  consumer that this tool *writes to* and never reads truth from.

---

## 4. Install

The controller stays stdlib-only; these pip-installable tools form a chain.
Install in order (each depends on the previous):

```bash
pip install -e tools/tact      # image/tactile deps (opencv, reportlab, …)
pip install -e tools/tasc      # the model + protocol this tool reuses
pip install -e tools/rhino-driver
```

> **Lightweight alternative** (just to render/inspect/test without the heavy
> `tact` stack): the renderer and tests only need the standard library plus
> `tasc` on the path. You can run them with
> `PYTHONPATH=tools/tasc/src:tools/rhino-driver/src` and `pip install pytest click`.

---

## 5. Test drive A — no Rhino required (works anywhere)

This track proves the engine end-to-end **without Rhino** — ideal for CI, a
Linux box, or before you install Rhino. It uses the `tasc` CLI to build a model,
then `rhino-driver` to render and diagnose.

### A1. Build a model with TASC

```bash
mkdir /tmp/rdemo && cd /tmp/rdemo
tasc site 200 150
tasc zone living 50 40 --at 10,10
tasc bay A 6x3 --spacing 24 24 --at 18,8
tasc describe
```

This writes `.tasc_state.json` in the current directory — the model
`rhino-driver` consumes.

### A2. Ask where Rhino is (expect: offline, with guidance)

```bash
rhino-driver status
```

Expected (no Rhino on this machine):

```
ERROR: Rhino not reachable (offline).
Socket: no at 127.0.0.1:1999.
rhinocode: not found.
Instances: none.
Next: No Rhino connection. Install Rhino 8 and ensure 'rhinocode' is on PATH
(macOS: /Applications/Rhino 8.app/Contents/Resources/bin), then run
StartScriptServer in Rhino. Or start the RhinoMCP plugin for the socket.
READY:
```

Every line is labeled and the `Next:` line is the exact remediation. This is the
anti-silent-failure behavior.

### A3. Generate the script and read it

```bash
rhino-driver render --out model.py
cat model.py
```

You'll see a complete full rebuild: clear the eight `TASC_*` layers, recreate
them, switch the viewport to **LightPen**, then draw. An excerpt:

```python
# Generated by rhino-driver: deterministic full rebuild of the TASC model.
import rhinoscriptsyntax as rs

for layer in ['TASC_Labels', 'TASC_Zones', 'TASC_Grid', 'TASC_Site', 'TASC_Bays',
              'TASC_Columns', 'TASC_Corridors', 'TASC_Voids']:
    objs = rs.ObjectsByLayer(layer)
    if objs:
        rs.DeleteObjects(objs)

if not rs.IsLayer("TASC_Site"): rs.AddLayer("TASC_Site", [0, 0, 0])
...
rs.CurrentLayer("TASC_Site")
_id = rs.AddPolyline([[0, 0, 0], [200, 0, 0], [200, 150, 0], [0, 150, 0], [0, 0, 0]])
if _id: rs.ObjectName(_id, "site_boundary")
if _id: rs.ObjectColor(_id, [0, 0, 0])
...
_id = rs.AddTextDot("living", [35.0, 30.0, 0])
```

### A4. Prove the script is always valid Python

The translator must never emit broken source, even for hostile names:

```bash
rhino-driver render --stdout | python3 -c "import sys; compile(sys.stdin.read(),'<gen>','exec'); print('OK: compiles')"
```

Try a nasty name and confirm it still compiles:

```bash
tasc zone "O'Brien \"Wing\"" 20 20 --at 5,5
rhino-driver render --stdout | python3 -c "import sys; compile(sys.stdin.read(),'<gen>','exec'); print('OK: still compiles')"
```

### A5. Try to draw while offline (expect: loud failure, not silence)

```bash
rhino-driver draw ; echo "exit=$?"
```

```
ERROR: not connected to Rhino; nothing drawn. Run 'rhino-driver status'.
READY:
exit=1
```

`draw` returns a non-zero exit code when it could not draw — honest for scripts
and CI, and audibly an error for a screen reader.

---

## 6. Test drive B — macOS with Rhino 8 (the headline path)

This is the path the project was missing. Rhino 8 for macOS is a shipping product
and includes `rhinocode`.

### B1. Put `rhinocode` on your PATH

```bash
export PATH="/Applications/Rhino 8.app/Contents/Resources/bin:$PATH"
rhinocode --help        # sanity check; confirm 'list' and 'script' subcommands
```

(If you skip this, `rhino-driver` will still auto-detect the bundle path, but
having it on `PATH` makes `rhinocode list` easy to run by hand.)

### B2. Start the script server inside Rhino

Open Rhino 8, and at the Rhino command line type:

```
StartScriptServer
```

This is **required** and is per-session. It's the macOS analogue of loading the
watcher on Windows. Confirm Rhino sees it:

```bash
rhinocode list          # should show an instance id like rhinocode_remotepipe_#####
```

### B3. Confirm the link

```bash
rhino-driver status
```

Expected:

```
OK: Rhino reachable via rhinocode.
Socket: no at 127.0.0.1:1999.
rhinocode: /Applications/Rhino 8.app/Contents/Resources/bin/rhinocode.
Instances: rhinocode_remotepipe_75029.
Next: Connected via rhinocode (instance rhinocode_remotepipe_75029).
READY:
```

### B4. Draw the model (one script, one run)

```bash
cd /tmp/rdemo
rhino-driver draw
```

```
OK: model drawn in Rhino (rhinocode).
READY:
```

Switch to Rhino: you'll see the site boundary, the 6×3 bay with its column grid,
and the `living` zone with a text-dot label, all on `TASC_*` layers, in LightPen
mode. Behind the scenes this was **one** `rhinocode script` call running **one**
generated script — not dozens of round trips.

### B5. Edit, redraw, and watch the full rebuild

```bash
tasc bay A --rotation 15
rhino-driver draw
```

Because every `draw` is a deterministic **full rebuild** (clear `TASC_*` then
recreate), the old, un-rotated bay is *gone* — there is never stale, duplicated
geometry. This is the same guarantee the Windows watcher gives.

### B6. Capture for tactile output, then export

```bash
# Capture is part of TASC; the working/captured display modes are already set.
tasc capture top.png --viewport Top
tact convert top.png --preset architecture --verbose
# or render the model straight to a tactile PDF:
tasc export piaf -o demo.pdf
```

### B7. Clear, and prove failure is loud

```bash
rhino-driver clear            # removes TASC geometry: "OK: TASC geometry cleared in Rhino (rhinocode)."
```

Now stop the script server in Rhino (or quit Rhino) and try again:

```bash
rhino-driver draw ; echo "exit=$?"
```

```
ERROR: not connected to Rhino; nothing drawn. Run 'rhino-driver status'.
READY:
exit=1
```

```bash
rhino-driver status           # 'rhinocode found but no live script server… run StartScriptServer'
```

The diagnosis distinguishes *binary missing* from *server not started* — the two
most common macOS snags.

---

## 7. Test drive C — Windows / WSL2 over the RhinoMCP socket

If you run the [RhinoMCP plugin](https://github.com/jingcheng-chen/rhinomcp) the
driver uses the socket instead, and the same whole-model script is sent as a
**single** `execute_rhinoscript_python_code` command.

1. In Rhino, start the RhinoMCP plugin (listens on `127.0.0.1:1999`).
2. From the same machine: `rhino-driver status` → `OK: Rhino reachable via mcp.`
3. `rhino-driver draw` → `OK: model drawn in Rhino (mcp).`

**WSL2 (Rhino on Windows, driver in WSL2):** the socket bound to `127.0.0.1` on
Windows isn't reachable from WSL2, so the driver auto-detects the Windows gateway
IP and retries there. One-time Windows setup:

```powershell
netsh interface portproxy add v4tov4 listenport=1999 listenaddress=0.0.0.0 connectport=1999 connectaddress=127.0.0.1
netsh advfirewall firewall add rule name="RhinoMCP" dir=in action=allow protocol=TCP localport=1999
```

`rhino-driver status` will then report `Environment: WSL2 …` and the gateway host.

**The N→1 win:** a model with a site, a 6×3 bay (28 columns), and a zone is dozens
of objects. The old socket path sent a `get_or_set_current_layer` + `create_object`
for *each* — dozens of blocking round trips. `rhino-driver` sends exactly one
message. (This invariant is locked down by a unit test; see §12.)

---

## 8. Command reference

All commands print labeled lines, an `OK:`/`ERROR:` prefix, and end with `READY:`.

### `rhino-driver status` (alias `doctor`)
Probe every transport and recommend the next action. Never fails.
Options: `--host` (default `127.0.0.1`), `--port` (default `1999`).

### `rhino-driver draw`
Full-rebuild the current model in Rhino as one script. Exit 0 on success, 1 if it
could not draw (offline/error).
Options: `--state` (default `.tasc_state.json`), `--host`, `--port`.

### `rhino-driver clear`
Remove all `TASC_*` geometry from Rhino (layer-scoped; leaves your other objects
alone). Options: `--host`, `--port`.

### `rhino-driver render`
Generate the RhinoPython script **without** running it — for review, offline use,
or manual execution (`rhinocode script <out>`).
Options: `--state`, `--out` (default `tasc_rhino_model.py`), `--stdout`.

---

## 9. Environment variables & exit codes

| Variable | Meaning | Default |
|----------|---------|---------|
| `TASC_RHINO_TIMEOUT` | Per-call `rhinocode` timeout, seconds | `60` |

| Exit code | Meaning |
|-----------|---------|
| `0` | Command succeeded (drew/cleared/rendered, or `status` ran). |
| `1` | `draw`/`clear` could not reach Rhino, or no model/state file found. |

---

## 10. Troubleshooting

| `status` says… | Cause | Fix |
|----------------|-------|-----|
| `rhinocode: not found.` | Rhino 8 not installed, or binary not on PATH | Install Rhino 8; `export PATH="/Applications/Rhino 8.app/Contents/Resources/bin:$PATH"` |
| `rhinocode found … no live script server` | Server not started | In Rhino: `StartScriptServer` |
| `Instances: none.` after `StartScriptServer` | Multiple Rhinos / stale pipe | `rhinocode list`; restart Rhino; re-run `StartScriptServer` |
| `Socket: no` but you run RhinoMCP | Plugin not listening / wrong port | Start RhinoMCP; check `--port` (default 1999) |
| WSL2: socket unreachable | No portproxy | Add the `netsh` portproxy rule (see §7) |
| `draw` says `no model found` | No `.tasc_state.json` here | Build a model first (`tasc site …`) or pass `--state` |
| `rhinocode timed out` | Very large model / slow machine | Raise `TASC_RHINO_TIMEOUT` |

---

## 11. How it fits the rest of RAP

- **TASC** (`tools/tasc/`) owns the *model* (site, grid, zones, bays) and the
  *protocol*. `rhino-driver` reuses both and adds the cross-platform *push to
  Rhino* step. Workflow: edit with `tasc …`, visualize with `rhino-driver draw`.
- **TACT** (`tools/tact/`) turns captured viewports or the model into tactile
  PIAF PDFs. After `rhino-driver draw`, capture and convert (§B6).
- **Controller + watcher** (`controller/`, `tools/rhino/`) remain the Windows
  path: `state.json` → IronPython watcher. `rhino-driver` is the cross-platform
  complement, and the recommended way to reach Rhino 8 on macOS.

This tool is **additive**: it leaves `tools/tasc/src/tasc/rhino/` untouched and
imports what it needs.

---

## 12. Running and reading the test suite

```bash
cd tools/rhino-driver
pytest
```

The suite needs no Rhino. What each part proves:

- **`test_render.py`** — every protocol command produces real `rs.*` calls; the
  full model renders site/bay/columns/label/**circle**; and **every** generated
  script `compile()`s, including with apostrophes, embedded quotes, newlines, and
  Braille in names. This is the direct guard against the two original bugs.
- **`test_rhinocode.py`** — the binary is found on PATH or in the macOS bundle;
  `rhinocode list` output is parsed into instance ids; `run_script` builds the
  correct argv (`<exe> --rhino <id> script <tempfile>`) and writes the script to
  the temp file; a non-zero return becomes an **error**, not a fake "ok".
- **`test_driver.py`** — against a mock socket server, a full-model redraw sends
  **exactly one** `execute_rhinoscript_python_code` command (the N→1 invariant);
  offline `run_model` reports `offline` with "nothing was drawn" (never a false
  success); and `status()` returns the right mode + remediation for the offline,
  binary-but-no-server, and live cases.
