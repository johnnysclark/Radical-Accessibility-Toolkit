"""rhino-driver CLI: push the current TASC model to Rhino, or diagnose the link.

Workflow on any platform::

    tasc site 200 150            # edit the model (writes .tasc_state.json)
    tasc zone living 50 40 --at 10,10
    rhino-driver status          # is Rhino reachable? what should I do?
    rhino-driver draw            # full-rebuild the model in Rhino, once

Output follows the project's screen-reader rules: short labeled lines, every
command prefixed ``OK:`` or ``ERROR:``, terminated by ``READY:`` so a screen
reader detects the state change. Nothing fails silently.
"""

from __future__ import annotations

from pathlib import Path

import click

from rhino_driver import __version__
from rhino_driver.driver import RhinoDriver
from rhino_driver.render import CollectingConnector, render_model

DEFAULT_STATE = ".tasc_state.json"


def _load_model(state: str):
    """Load a TASC model from a state file, or return None if absent."""
    from tasc.core.model import TASCModel

    path = Path(state)
    if not path.exists():
        return None
    return TASCModel.load(path)


def _echo(line: str) -> None:
    click.echo(line)


def _ready() -> None:
    click.echo("READY:")


@click.group()
@click.version_option(version=__version__, prog_name="rhino-driver")
def main():
    """Accessible CLI driver: render a TASC model to Rhino as one deterministic script."""


@main.command(name="status")
@click.option("--host", default="127.0.0.1", help="RhinoMCP socket host")
@click.option("--port", default=1999, type=int, help="RhinoMCP socket port")
def status_cmd(host, port):
    """Report how Rhino is reachable and the exact next step. (alias: doctor)"""
    info = RhinoDriver(host=host, port=port).status()
    mode = info["mode"]
    if mode in ("mcp", "rhinocode"):
        _echo("OK: Rhino reachable via {0}.".format(mode))
    else:
        _echo("ERROR: Rhino not reachable (offline).")

    sock = "yes" if info["socket_reachable"] else "no"
    _echo("Socket: {0} at {1}:{2}.".format(sock, info["socket_host"], info["socket_port"]))
    _echo("rhinocode: {0}.".format(info["rhinocode_path"] if info["rhinocode_found"] else "not found"))
    instances = info["rhinocode_instances"]
    _echo("Instances: {0}.".format(", ".join(instances) if instances else "none"))
    if info["wsl2"]:
        _echo("Environment: WSL2 (Rhino on Windows host).")
    _echo("Next: {0}".format(info["recommendation"]))
    _ready()


# 'doctor' as a friendly alias for 'status'.
main.add_command(status_cmd, name="doctor")


@main.command(name="draw")
@click.option("--state", default=DEFAULT_STATE, help="TASC state file to render")
@click.option("--host", default="127.0.0.1", help="RhinoMCP socket host")
@click.option("--port", default=1999, type=int, help="RhinoMCP socket port")
def draw_cmd(state, host, port):
    """Full-rebuild the current model in Rhino (one script, one round trip)."""
    model = _load_model(state)
    if model is None:
        _echo("ERROR: no model found at {0}. Build one with 'tasc site ...' first.".format(state))
        _ready()
        raise SystemExit(1)

    driver = RhinoDriver(host=host, port=port)
    driver.connect()
    result = driver.run_model(model)
    driver.disconnect()

    status = result.get("status")
    mode = result.get("mode", "offline")
    output = (result.get("output") or "").strip()

    if status == "ok":
        _echo("OK: model drawn in Rhino ({0}).".format(mode))
    elif status == "offline":
        _echo("ERROR: not connected to Rhino; nothing drawn. Run 'rhino-driver status'.")
    else:
        detail = ": {0}".format(output) if output else ""
        _echo("ERROR: Rhino draw failed ({0}){1}".format(mode, detail))
    _ready()
    if status != "ok":
        raise SystemExit(1)


@main.command(name="clear")
@click.option("--host", default="127.0.0.1", help="RhinoMCP socket host")
@click.option("--port", default=1999, type=int, help="RhinoMCP socket port")
def clear_cmd(host, port):
    """Remove all TASC geometry from Rhino (layer-scoped)."""
    from tasc.rhino.commands import RhinoDrawer

    collector = CollectingConnector()
    RhinoDrawer(collector).clear_all()

    driver = RhinoDriver(host=host, port=port)
    driver.connect()
    result = driver.apply(collector.commands)
    driver.disconnect()

    status = result.get("status")
    mode = result.get("mode", "offline")
    if status == "ok":
        _echo("OK: TASC geometry cleared in Rhino ({0}).".format(mode))
    elif status == "offline":
        _echo("ERROR: not connected to Rhino; nothing cleared. Run 'rhino-driver status'.")
    else:
        _echo("ERROR: clear failed ({0}): {1}".format(mode, (result.get("output") or "").strip()))
    _ready()
    if status != "ok":
        raise SystemExit(1)


@main.command(name="render")
@click.option("--state", default=DEFAULT_STATE, help="TASC state file to render")
@click.option("--out", "out", default="tasc_rhino_model.py", help="Output script path")
@click.option("--stdout", "to_stdout", is_flag=True, help="Print the script to stdout instead of a file")
def render_cmd(state, out, to_stdout):
    """Generate the RhinoPython script for the model without running it.

    Useful offline, for review, or to run by hand: rhinocode script <out>.
    """
    model = _load_model(state)
    if model is None:
        _echo("ERROR: no model found at {0}. Build one with 'tasc site ...' first.".format(state))
        _ready()
        raise SystemExit(1)

    script = render_model(model)
    if to_stdout:
        click.echo(script)
        return

    Path(out).write_text(script, encoding="utf-8")
    _echo("OK: wrote script to {0}.".format(out))
    _echo("Run it manually with: rhinocode script {0}".format(out))
    _ready()


if __name__ == "__main__":
    main()
