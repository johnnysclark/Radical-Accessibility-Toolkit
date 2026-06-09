# rhino-driver

Accessible command-line driver that renders a **TASC** model to **Rhino** as one
deterministic RhinoPython script. It fixes and supersedes the previous macOS path,
and unifies the two live transports behind a single full-rebuild script:

- **macOS** — the real `rhinocode` CLI (`rhinocode script <file>`), Rhino 8's
  script-server tool. (The old code called a non-existent `rhinocode exec --code`
  and translated commands with the wrong shape, so it drew nothing.)
- **Windows / WSL2** — the RhinoMCP socket, sent as a single
  `execute_rhinoscript_python_code` command (one round trip instead of hundreds).

If neither is available the driver is **offline** and says so — loudly. It never
reports success while nothing was drawn.

> **New here? Read [MANUAL.md](MANUAL.md)** for a detailed, step-by-step test
> drive (with and without Rhino) and a full explanation of how it works.

## Why one script?

The Layout Jig watcher already proved the right model: *same state → one
deterministic full rebuild*. This tool brings that to the cross-platform path.
Instead of pushing one socket command per object (slow, and on macOS broken), it
collects the whole model into one ordered command list — reusing TASC's existing
geometry in `tasc.rhino.commands.RhinoDrawer`, so nothing is duplicated — and
translates it into one script that clears prior TASC geometry and redraws
everything. The same script runs over any transport, is auditable, and is atomic.

## Install

Install the dependency chain in order (the controller stays stdlib-only; these are
the pip-allowed tools):

```bash
pip install -e tools/tact
pip install -e tools/tasc
pip install -e tools/rhino-driver
```

## macOS setup (the path this tool unlocks)

Rhino 8 for macOS is a real, shipping product and includes `rhinocode`.

1. Install **Rhino 8**.
2. Put `rhinocode` on your `PATH` (or rely on auto-detection of the bundle path):
   ```bash
   export PATH="/Applications/Rhino 8.app/Contents/Resources/bin:$PATH"
   ```
3. Open Rhino, and at the command line run **`StartScriptServer`** once per session.
   (The script server is not started automatically.)
4. Verify:
   ```bash
   rhino-driver status
   ```
   Expect `OK: Rhino reachable via rhinocode.` and a live instance id.

## Usage

`rhino-driver` consumes the model that the `tasc` CLI writes to `.tasc_state.json`:

```bash
tasc site 200 150                       # edit the model (TASC)
tasc zone living 50 40 --at 10,10
tasc bay A 6x3 --spacing 24 24

rhino-driver status                     # is Rhino reachable? what to do next?
rhino-driver draw                       # full-rebuild the model in Rhino, once
rhino-driver clear                      # remove TASC geometry from Rhino
rhino-driver render --out model.py      # just generate the script (no Rhino needed)
```

Every command prints short labeled lines, an `OK:`/`ERROR:` prefix, and a
terminating `READY:` for screen-reader detection.

### Options

- `--host` / `--port` — RhinoMCP socket endpoint (default `127.0.0.1:1999`).
- `--state` — TASC state file (default `.tasc_state.json`).
- `TASC_RHINO_TIMEOUT` — per-call `rhinocode` timeout in seconds (default `60`).

## How it connects

`rhino-driver` tries, in order:

1. RhinoMCP socket at `--host:--port`.
2. (WSL2 only) the Windows-host gateway IP, auto-detected.
3. `rhinocode` — **only if a live script-server instance exists**, so it never
   selects a transport that would quietly do nothing.
4. Offline — reported clearly, with the exact next step.

## Tests

```bash
cd tools/rhino-driver
pytest
```

The suite runs without Rhino. It compiles every generated script (proving the
translation and string-escaping are always valid Python), checks the real
`rhinocode` argv/`list` parsing with a mocked subprocess, and asserts the N→1
invariant (a full-model redraw sends exactly one socket command) against a mock
server.

## Relationship to the existing code

This is a standalone, additive tool. It leaves `tools/tasc/src/tasc/rhino/`
untouched and reuses `tasc.core.model`, `tasc.rhino.protocol`, and
`tasc.rhino.commands` by import. The intent is for it to become the recommended
cross-platform way to push a TASC model into Rhino.
