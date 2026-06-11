"""Snapshot cache: fast state loading without replaying the whole journal.

The snapshot is a derived cache, never truth. Loading state means:
read snapshot (if any and consistent), then replay journal entries
newer than its upto_seq. Deleting snapshot.json loses nothing.
"""

from __future__ import annotations

import json
import os

from maquette import SNAPSHOT_SCHEMA
from maquette import journal as journal_mod
from maquette.project import Project, atomic_write
from maquette.scene import Scene

SNAPSHOT_EVERY = 25  # ops between automatic snapshot writes


def load_scene(project: Project) -> Scene:
    """Derive the current scene: snapshot plus journal tail."""
    scene = _load_snapshot(project)
    if scene is None:
        scene = Scene(project.name, project.units)
    for entry in journal_mod.read_entries(project.journal_path, scene.applied_seq):
        scene.apply(entry)
    return scene


def replay_scene(project: Project, upto_seq: int | None = None) -> Scene:
    """Derive the scene from the journal alone (no snapshot)."""
    scene = Scene(project.name, project.units)
    for entry in journal_mod.read_entries(project.journal_path):
        if upto_seq is not None and entry["seq"] > upto_seq:
            break
        scene.apply(entry)
    return scene


def write_snapshot(project: Project, scene: Scene) -> None:
    atomic_write(project.snapshot_path,
                 json.dumps(scene.to_dict(), indent=2) + "\n")


def maybe_write_snapshot(project: Project, scene: Scene) -> bool:
    """Write the snapshot when it has fallen SNAPSHOT_EVERY ops behind."""
    on_disk = _snapshot_seq(project)
    if scene.applied_seq - on_disk >= SNAPSHOT_EVERY:
        write_snapshot(project, scene)
        return True
    return False


def _load_snapshot(project: Project) -> Scene | None:
    try:
        with open(project.snapshot_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    if data.get("schema") != SNAPSHOT_SCHEMA:
        return None
    # A snapshot ahead of the journal means the journal was replaced or
    # truncated; the journal wins, so discard the stale cache.
    if data.get("upto_seq", 0) > journal_mod.last_seq(project.journal_path):
        return None
    return Scene.from_dict(data)


def _snapshot_seq(project: Project) -> int:
    try:
        with open(project.snapshot_path, "r", encoding="utf-8") as handle:
            return json.load(handle).get("upto_seq", 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def drop_snapshot(project: Project) -> None:
    if os.path.exists(project.snapshot_path):
        os.remove(project.snapshot_path)
