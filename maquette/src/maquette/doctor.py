"""maquette doctor: ordered checks, each with the exact fix.

Also: maquette connect (check or revive the Rhino link, optionally
injecting the listener through rhinocode) and maquette listener-stop.
"""

from __future__ import annotations

import importlib
import os
import shutil
import sys
import time

from maquette import DEFAULT_HOST, DEFAULT_PORT, say
from maquette import journal as journal_mod
from maquette import rhinocode
from maquette.backends.base import BackendError
from maquette.netclient import ListenerClient
from maquette.project import ProjectError, find_project


def _address(flags: dict):
    try:
        project = find_project(flags.get("project"))
        return project, project.listener_address
    except ProjectError:
        return None, (DEFAULT_HOST, DEFAULT_PORT)


def run(flags: dict, payload: dict) -> int:
    errors = 0
    project, (host, port) = _address(flags)

    if sys.version_info >= (3, 10):
        say.ok("Python {0}.{1}.{2}.".format(*sys.version_info[:3]))
    else:
        errors += 1
        say.err("Python {0}.{1} is too old.".format(*sys.version_info[:2]))
        say.info("fix: install Python 3.10 or newer and reinstall maquette.")

    if project is not None:
        entries = list(journal_mod.read_entries(project.journal_path))
        say.ok("project {0} at {1}: {2} journal steps.".format(
            project.name, project.root, len(entries)))
    else:
        say.warn("not inside a maquette project; project checks skipped.")
        say.info("fix: cd into a project, or run: maquette init NAME")

    for package, extra, why in (
            ("rhino3dm", "headless", "build 3dm files without Rhino"),
            ("mcp", "mcp", "let Claude Code drive maquette"),
            ("claude_agent_sdk", "chat", "talk to Claude with maquette chat")):
        try:
            importlib.import_module(package)
            say.ok("{0} installed.".format(package))
        except ImportError:
            say.warn("{0} not installed; needed to {1}.".format(package, why))
            say.info("fix: pip install 'maquette[{0}]'".format(extra))

    if _chat_auth_present():
        say.ok("Claude credentials found for the chat REPL.")
    else:
        say.warn("no Claude credentials found for maquette chat.")
        say.info("fix: sign in once with the Claude Code app (claude login),")
        say.info("or run: claude setup-token, or set ANTHROPIC_API_KEY.")

    binary = rhinocode.find_rhinocode()
    if binary:
        say.ok("rhinocode CLI at {0}.".format(binary))
    elif sys.platform == "darwin":
        say.warn("rhinocode CLI not found; recovery via maquette connect "
                 "--inject will not work.")
        say.info("fix: install Rhino 8.11 or newer.")
    else:
        say.info("rhinocode: not a Mac, skipped (Rhino runs on the Mac).")

    if _listener_check(host, port):
        pass
    else:
        errors += 1

    if errors:
        say.err("{0} problem(s) above need fixing.".format(errors))
        payload["ok"] = False
        return 1
    say.ok("everything looks good.")
    return 0


def _chat_auth_present() -> bool:
    return bool(os.environ.get("CLAUDE_CODE_OAUTH_TOKEN")
                or os.environ.get("ANTHROPIC_API_KEY")
                or shutil.which("claude"))


def _listener_check(host: str, port: int) -> bool:
    client = ListenerClient(host, port)
    try:
        info = client.connect()
        say.ok("Rhino listener on {0} port {1}: Rhino {2}, document {3}.".format(
            host, port, info.get("rhino", "?"), info.get("doc", "?")))
        client.close()
        return True
    except BackendError:
        say.err("no Rhino listener on {0} port {1}.".format(host, port))
        say.info("fix, in order:")
        say.info("1. Is Rhino 8 running on this Mac? Start it.")
        say.info("2. First time? Run: maquette install-listener")
        say.info("3. Listener installed but not running? Run: "
                 "maquette connect --inject")
        say.info("4. Modeling without Rhino is fine too: commands are "
                 "journaled and maquette rebuild catches Rhino up later.")
        return False


def connect(flags: dict, payload: dict) -> int:
    project, (host, port) = _address(flags)
    if _listener_check(host, port):
        return 0
    if flags.get("inject"):
        from maquette.install import install
        say.info("trying to start the listener through rhinocode.")
        instances = rhinocode.list_instances()
        if not instances and rhinocode.find_rhinocode() is None:
            say.err("rhinocode CLI not found; cannot inject.")
            payload["ok"] = False
            return 1
        script_path = install(flags.get("dest"))
        ok, output = rhinocode.run_script(script_path)
        if not ok:
            say.err("rhinocode could not run the listener: {0}".format(
                output or "no output"))
            say.info("fix: in Rhino, run the command StartScriptServer once, "
                     "then retry. Or restart Rhino.")
            payload["ok"] = False
            return 1
        time.sleep(1.0)
        if _listener_check(host, port):
            return 0
    payload["ok"] = False
    return 1


def listener_stop(flags: dict, payload: dict) -> int:
    _project, (host, port) = _address(flags)
    client = ListenerClient(host, port)
    try:
        client.connect()
        client.request("shutdown", {})
        say.ok("asked the listener on port {0} to stop.".format(port))
        client.close()
        return 0
    except BackendError:
        say.ok("no listener running on port {0}; nothing to stop.".format(port))
        return 0
