"""Tests for the real ``rhinocode`` CLI wrapper (argv, discovery, escaping-free file path)."""

from pathlib import Path

from rhino_driver import rhinocode
from rhino_driver.rhinocode import RhinoCodeCLI, find_rhinocode


class FakeProc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class TestFindRhinocode:
    def test_prefers_path(self, monkeypatch):
        monkeypatch.setattr(rhinocode.shutil, "which", lambda _: "/usr/local/bin/rhinocode")
        assert find_rhinocode() == "/usr/local/bin/rhinocode"

    def test_falls_back_to_mac_bundle(self, monkeypatch):
        monkeypatch.setattr(rhinocode.shutil, "which", lambda _: None)
        bundle = rhinocode.MAC_BIN_CANDIDATES[0]
        monkeypatch.setattr(rhinocode.os.path, "isfile", lambda p: p == bundle)
        assert find_rhinocode() == bundle

    def test_none_when_absent(self, monkeypatch):
        monkeypatch.setattr(rhinocode.shutil, "which", lambda _: None)
        monkeypatch.setattr(rhinocode.os.path, "isfile", lambda _: False)
        assert find_rhinocode() is None


class TestListInstances:
    def test_parses_instance_ids(self, monkeypatch):
        out = "Running Rhino instances:\n  rhinocode_remotepipe_75029  Rhino 8\n"
        monkeypatch.setattr(rhinocode.subprocess, "run", lambda *a, **k: FakeProc(stdout=out))
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        assert cli.list_instances() == ["rhinocode_remotepipe_75029"]
        assert cli.has_live_instance() is True

    def test_empty_when_no_server(self, monkeypatch):
        monkeypatch.setattr(rhinocode.subprocess, "run", lambda *a, **k: FakeProc(stdout="No instances\n"))
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        assert cli.list_instances() == []
        assert cli.has_live_instance() is False

    def test_no_binary_returns_empty(self):
        cli = RhinoCodeCLI(exe=None)
        assert cli.found is False
        assert cli.list_instances() == []


class TestRunScript:
    def test_argv_and_tempfile(self, monkeypatch):
        captured = {}

        def fake_run(argv, **kwargs):
            captured["argv"] = argv
            captured["content"] = Path(argv[-1]).read_text(encoding="utf-8")
            return FakeProc(stdout="ok", returncode=0)

        monkeypatch.setattr(rhinocode.subprocess, "run", fake_run)
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        result = cli.run_script("print(1)", instance_id="rhinocode_remotepipe_1")

        assert captured["argv"][0] == "/fake/rhinocode"
        assert captured["argv"][1:3] == ["--rhino", "rhinocode_remotepipe_1"]
        assert captured["argv"][3] == "script"
        assert captured["argv"][4].endswith(".py")
        assert captured["content"] == "print(1)"
        assert result["status"] == "ok"
        assert result["returncode"] == 0

    def test_auto_discovers_instance(self, monkeypatch):
        captured = {}

        def fake_run(argv, **kwargs):
            # First call is `list`, subsequent is `script`.
            if argv[-1] == "list":
                return FakeProc(stdout="rhinocode_remotepipe_42\n")
            captured["argv"] = argv
            return FakeProc(stdout="done", returncode=0)

        monkeypatch.setattr(rhinocode.subprocess, "run", fake_run)
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        cli.run_script("print(1)")  # no explicit instance -> auto-discover
        assert "--rhino" in captured["argv"]
        assert "rhinocode_remotepipe_42" in captured["argv"]

    def test_nonzero_is_error_not_silent_ok(self, monkeypatch):
        monkeypatch.setattr(
            rhinocode.subprocess,
            "run",
            lambda *a, **k: FakeProc(stdout="", stderr="boom", returncode=1),
        )
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        result = cli.run_script("print(1)", instance_id="x")
        assert result["status"] == "error"
        assert "boom" in result["output"]

    def test_missing_binary_is_error(self):
        cli = RhinoCodeCLI(exe=None)
        result = cli.run_script("print(1)")
        assert result["status"] == "error"


class TestTimeout:
    def test_env_override(self, monkeypatch):
        monkeypatch.setenv("TASC_RHINO_TIMEOUT", "5")
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        assert cli.timeout == 5.0

    def test_default(self, monkeypatch):
        monkeypatch.delenv("TASC_RHINO_TIMEOUT", raising=False)
        cli = RhinoCodeCLI(exe="/fake/rhinocode")
        assert cli.timeout == rhinocode.DEFAULT_TIMEOUT
