"""Project folders: creation, discovery, atomic writes, single-writer lock.

A project is a folder containing maquette.json, journal.jsonl,
snapshot.json, exports/ and transcripts/. Discovery walks upward from
the working directory like git. The lock is advisory flock on
journal.lock so two writers cannot interleave journal appends.
"""

from __future__ import annotations

import contextlib
import datetime
import json
import os

from maquette import DEFAULT_HOST, DEFAULT_PORT, PROJECT_SCHEMA

try:
    import fcntl
except ImportError:  # non-POSIX; Maquette targets macOS and Linux
    fcntl = None

PROJECT_FILE = "maquette.json"
JOURNAL_FILE = "journal.jsonl"
SNAPSHOT_FILE = "snapshot.json"
LOCK_FILE = "journal.lock"


class ProjectError(Exception):
    pass


def atomic_write(path: str, text: str) -> None:
    """Write text to path atomically: temp file, fsync, replace."""
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Project:
    def __init__(self, root: str):
        self.root = os.path.abspath(root)
        self.meta_path = os.path.join(self.root, PROJECT_FILE)
        self.journal_path = os.path.join(self.root, JOURNAL_FILE)
        self.snapshot_path = os.path.join(self.root, SNAPSHOT_FILE)
        self.lock_path = os.path.join(self.root, LOCK_FILE)
        self.exports_dir = os.path.join(self.root, "exports")
        self.transcripts_dir = os.path.join(self.root, "transcripts")
        self.meta = self._load_meta()

    def _load_meta(self) -> dict:
        try:
            with open(self.meta_path, "r", encoding="utf-8") as handle:
                meta = json.load(handle)
        except FileNotFoundError:
            raise ProjectError(
                "no maquette project at {0}. Run: maquette init NAME".format(self.root))
        except json.JSONDecodeError as exc:
            raise ProjectError("maquette.json is not valid JSON: {0}".format(exc))
        # Schema migration hook: add new fields with defaults, never break old files.
        meta.setdefault("schema", PROJECT_SCHEMA)
        meta.setdefault("units", "meters")
        meta.setdefault("listener", {"host": DEFAULT_HOST, "port": DEFAULT_PORT})
        meta.setdefault("backend", "auto")
        return meta

    def save_meta(self) -> None:
        atomic_write(self.meta_path, json.dumps(self.meta, indent=2) + "\n")

    @property
    def name(self) -> str:
        return self.meta.get("name", os.path.basename(self.root))

    @property
    def units(self) -> str:
        return self.meta.get("units", "meters")

    @property
    def listener_address(self) -> tuple[str, int]:
        listener = self.meta.get("listener", {})
        return listener.get("host", DEFAULT_HOST), int(listener.get("port", DEFAULT_PORT))

    @contextlib.contextmanager
    def write_lock(self):
        """Exclusive advisory lock for journal mutations."""
        handle = open(self.lock_path, "a+")
        try:
            if fcntl is not None:
                try:
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                except OSError:
                    raise ProjectError(
                        "another maquette is writing to this project. "
                        "Wait for it to finish and retry.")
            yield
        finally:
            if fcntl is not None:
                with contextlib.suppress(OSError):
                    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
            handle.close()


def init_project(path: str, name: str | None = None, units: str = "meters") -> Project:
    root = os.path.abspath(path)
    meta_path = os.path.join(root, PROJECT_FILE)
    if os.path.exists(meta_path):
        raise ProjectError("a maquette project already exists at {0}".format(root))
    os.makedirs(root, exist_ok=True)
    os.makedirs(os.path.join(root, "exports"), exist_ok=True)
    os.makedirs(os.path.join(root, "transcripts"), exist_ok=True)
    meta = {
        "schema": PROJECT_SCHEMA,
        "name": name or os.path.basename(root),
        "units": units,
        "listener": {"host": DEFAULT_HOST, "port": DEFAULT_PORT},
        "backend": "auto",
        "created": utc_now(),
    }
    atomic_write(meta_path, json.dumps(meta, indent=2) + "\n")
    open(os.path.join(root, JOURNAL_FILE), "a", encoding="utf-8").close()
    return Project(root)


def find_project(start: str | None = None) -> Project:
    """Walk upward from start (default cwd) looking for maquette.json."""
    current = os.path.abspath(start or os.getcwd())
    while True:
        if os.path.exists(os.path.join(current, PROJECT_FILE)):
            return Project(current)
        parent = os.path.dirname(current)
        if parent == current:
            raise ProjectError(
                "no maquette project found here or above. Run: maquette init NAME")
        current = parent
