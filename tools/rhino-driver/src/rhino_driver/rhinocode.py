"""Run RhinoPython through Rhino 8's real ``rhinocode`` command-line tool.

The previous macOS path called ``rhinocode exec --code "<inline>"`` — a
subcommand and flag that do not exist. The real Rhino 8 CLI (Rhino >= 8.11) is::

    rhinocode list                                  # discover running instances
    rhinocode --rhino <instance-id> script <file.py>  # run a script file

and it requires the in-Rhino script server to be running first::

    StartScriptServer    (typed at the Rhino command line, once per session)

On macOS the binary ships inside the app bundle at
``/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode``; we auto-detect it
when it isn't already on ``PATH``.

References:
- https://developer.rhino3d.com/guides/scripting/advanced-cli/
- https://developer.rhino3d.com/guides/rhinopython/python-running-scripts/

The exact column layout of ``rhinocode list`` is not contractually documented, so
:meth:`RhinoCodeCLI.list_instances` parses defensively (any ``rhinocode_*`` token
on a line is treated as an instance id). Confirm with ``rhinocode list`` /
``rhinocode --help`` on the target machine if discovery ever comes up empty.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile

# macOS app-bundle locations to probe when ``rhinocode`` isn't on PATH.
MAC_BIN_CANDIDATES = [
    "/Applications/Rhino 8.app/Contents/Resources/bin/rhinocode",
    "/Applications/RhinoWIP.app/Contents/Resources/bin/rhinocode",
]

# Matches instance identifiers like "rhinocode_remotepipe_75029".
_INSTANCE_RE = re.compile(r"rhinocode_[A-Za-z0-9_]+")

DEFAULT_TIMEOUT = 60.0


def find_rhinocode() -> str | None:
    """Return the path to the ``rhinocode`` binary, or ``None`` if not found.

    Prefers ``PATH``; falls back to the known macOS app-bundle locations so the
    tool works out of the box on a stock Rhino 8 install.
    """
    on_path = shutil.which("rhinocode")
    if on_path:
        return on_path
    for candidate in MAC_BIN_CANDIDATES:
        if os.path.isfile(candidate):
            return candidate
    return None


def _resolve_timeout(timeout: float | None) -> float:
    if timeout is not None:
        return timeout
    env = os.environ.get("TASC_RHINO_TIMEOUT")
    if env:
        try:
            return float(env)
        except ValueError:
            pass
    return DEFAULT_TIMEOUT


class RhinoCodeCLI:
    """Thin wrapper around the ``rhinocode`` binary."""

    def __init__(self, exe: str | None = None, timeout: float | None = None):
        self.exe = exe or find_rhinocode()
        self.timeout = _resolve_timeout(timeout)

    @property
    def found(self) -> bool:
        """True if the ``rhinocode`` binary exists."""
        return self.exe is not None

    def list_instances(self) -> list[str]:
        """Return ids of running Rhino instances with a live script server.

        Empty list means either no Rhino is running or ``StartScriptServer`` has
        not been run. Returns ``[]`` on any failure rather than raising.
        """
        if not self.exe:
            return []
        try:
            result = subprocess.run(
                [self.exe, "list"],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except (OSError, subprocess.SubprocessError):
            return []
        text = (result.stdout or "") + "\n" + (result.stderr or "")
        # De-duplicate while preserving order.
        seen: list[str] = []
        for match in _INSTANCE_RE.findall(text):
            if match not in seen:
                seen.append(match)
        return seen

    def has_live_instance(self) -> bool:
        return bool(self.list_instances())

    def run_script(self, code: str, instance_id: str | None = None) -> dict:
        """Write ``code`` to a temp file and run it via ``rhinocode script``.

        Returns a structured result: ``{"status": "ok"|"error", "output": str,
        "returncode": int}``. Never raises for the caller's benefit — failures
        come back as ``status == "error"`` with the message in ``output`` so the
        CLI can surface them loudly (no silent success).
        """
        if not self.exe:
            return {"status": "error", "output": "rhinocode binary not found", "returncode": -1}

        if instance_id is None:
            instances = self.list_instances()
            instance_id = instances[0] if instances else None

        tmp = tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", prefix="rhino_driver_", delete=False, encoding="utf-8"
        )
        try:
            tmp.write(code)
            tmp.close()
            argv = [self.exe]
            if instance_id:
                argv += ["--rhino", instance_id]
            argv += ["script", tmp.name]
            try:
                result = subprocess.run(
                    argv,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                )
            except subprocess.TimeoutExpired:
                return {
                    "status": "error",
                    "output": "rhinocode timed out after {0}s".format(self.timeout),
                    "returncode": -1,
                }
            except OSError as exc:
                return {"status": "error", "output": "rhinocode failed: {0}".format(exc), "returncode": -1}

            output = (result.stdout or "") + (result.stderr or "")
            status = "ok" if result.returncode == 0 else "error"
            return {"status": status, "output": output.strip(), "returncode": result.returncode}
        finally:
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
