"""The watcher runs inside Rhino, but its compile + dispatch + report logic
is import-safe anywhere; only the rs calls need Rhino. A fake rs module
checks the drawing dispatch covers every primitive the compiler emits."""

import json

from jig.geometry.compile import compile_scene
from jig.watcher import jig_watcher


class FakeRS:
    def __init__(self):
        self.objects = []
        self.layers = set()
        self._next = 0

    def _add(self, kind):
        self._next += 1
        guid = "{}-{}".format(kind, self._next)
        self.objects.append(guid)
        return guid

    def AddLine(self, a, b):
        return self._add("line")

    def AddPolyline(self, points):
        return self._add("polyline")

    def AddCircle(self, center, radius):
        return self._add("circle")

    def AddArc3Pt(self, start, end, interior):
        return self._add("arc")

    def AddText(self, text, point, height):
        return self._add("text")

    def AddLayer(self, name):
        self.layers.add(name)
        return name

    def IsLayer(self, name):
        return name in self.layers

    def ObjectsByLayer(self, name):
        return []

    def DeleteObjects(self, objects):
        return len(objects)

    def ObjectLayer(self, guid, layer):
        return layer


def test_render_plan_draws_everything(school):
    plan = compile_scene(school.state)
    fake = FakeRS()
    drawn = jig_watcher.render_plan(fake, plan)
    total = sum(len(p) for p in plan.values())
    assert drawn == total
    assert len(fake.objects) == total
    assert "JIG::Columns" in fake.layers


def test_rebuild_writes_report_outside_rhino(school):
    report = jig_watcher.rebuild(school.state_path)
    assert report["error"] == ""
    assert report["counts"]["total"] > 0
    assert report["bbox"] is not None
    on_disk = json.load(open(jig_watcher.report_path(school.state_path)))
    assert on_disk["counts"] == report["counts"]


def test_rebuild_reports_bad_state(tmp_path):
    bad = tmp_path / "state.json"
    bad.write_text("{not json")
    report = jig_watcher.rebuild(str(bad))
    assert report["error"] != ""


def test_rhino_status_reads_report(school):
    jig_watcher.rebuild(school.state_path)
    message = school.execute("rhino status")
    assert "rebuilt" in message and "seconds ago" in message


def test_rhino_status_without_report(session):
    assert "no scene report" in session.execute("rhino status")


def test_install_bundle_is_self_contained(tmp_path, school, monkeypatch):
    from jig.commands import rhino as rhino_cmd
    monkeypatch.setattr(rhino_cmd, "support_dir", lambda: str(tmp_path / "support"))
    bundle = rhino_cmd.install_bundle(school)
    import os
    import subprocess
    import sys
    assert os.path.exists(os.path.join(bundle, "jig_watcher.py"))
    assert os.path.exists(os.path.join(bundle, "jig", "geometry", "compile.py"))
    assert os.path.exists(os.path.join(bundle, "jig", "model", "schema.py"))
    # the bundle must import and dry-run with ONLY itself on the path
    result = subprocess.run(
        [sys.executable, os.path.join(bundle, "jig_watcher.py")],
        capture_output=True, text=True,
        env={"PATH": os.environ.get("PATH", ""),
             "JIG_CONFIG": os.path.join(str(tmp_path / "support"), "config.json")},
    )
    assert result.returncode == 0, result.stderr
    assert "dry-run" in result.stdout
