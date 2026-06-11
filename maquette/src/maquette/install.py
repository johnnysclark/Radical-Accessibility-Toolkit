"""maquette install-listener: put the listener where Rhino finds it."""

from __future__ import annotations

import importlib.resources
import os

from maquette import DEFAULT_PORT, say
from maquette.project import atomic_write

MAC_SCRIPTS_DIR = os.path.expanduser(
    "~/Library/Application Support/McNeel/Rhinoceros/8.0/scripts")
LISTENER_NAME = "maquette_listener.py"


def listener_source() -> str:
    return (importlib.resources.files("maquette.listener")
            .joinpath(LISTENER_NAME).read_text(encoding="utf-8"))


def install(dest_dir: str | None = None) -> str:
    directory = dest_dir or MAC_SCRIPTS_DIR
    os.makedirs(directory, exist_ok=True)
    destination = os.path.join(directory, LISTENER_NAME)
    atomic_write(destination, listener_source())
    return destination


def run(flags: dict, payload: dict) -> int:
    destination = install(flags.get("dest"))
    say.ok("installed the Rhino listener at {0}".format(destination))
    say.info("One-time setup inside Rhino, four steps:")
    say.info("1. Open Rhino Settings, then the General page.")
    say.info("2. Add this startup command, all one line:")
    say.info('   _-ScriptEditor _R "{0}"'.format(destination))
    say.info("3. Optional but recommended, add a second startup command:")
    say.info("   _StartScriptServer")
    say.info("   It lets maquette restart the listener without the Rhino UI.")
    say.info("4. Restart Rhino. The command line says: "
             "[Maquette] Listening on 127.0.0.1:{0}.".format(DEFAULT_PORT))
    say.info("Then check everything with: maquette doctor")
    payload["lines"] = ["installed " + destination]
    return 0
