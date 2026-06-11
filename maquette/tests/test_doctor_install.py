"""doctor and install-listener behave well in a container with no Rhino."""

import os

from maquette import cli
from maquette.install import listener_source


def run_cli(capsys, *args):
    code = cli.main(list(args))
    captured = capsys.readouterr()
    return code, captured.out + captured.err


def test_doctor_degrades_gracefully(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("CLAUDE_CODE_OAUTH_TOKEN", raising=False)
    root = str(tmp_path / "site")
    run_cli(capsys, "init", "site", "--project", root)
    code, out = run_cli(capsys, "doctor", "--project", root)
    assert code == 1  # no listener here, and that is an ERROR with fixes
    assert "OK: Python" in out
    assert "OK: project site" in out
    assert "ERROR: no Rhino listener" in out
    assert "maquette install-listener" in out
    assert "maquette rebuild catches Rhino up later" in out
    assert out.rstrip().endswith("READY:")


def test_doctor_outside_project_still_runs(tmp_path, capsys, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code, out = run_cli(capsys, "doctor")
    assert "not inside a maquette project" in out
    assert code == 1


def test_install_listener_writes_identical_copy(tmp_path, capsys):
    dest_dir = str(tmp_path / "scripts")
    code, out = run_cli(capsys, "install-listener", "--dest", dest_dir)
    assert code == 0
    destination = os.path.join(dest_dir, "maquette_listener.py")
    assert "OK: installed the Rhino listener at" in out
    assert '_-ScriptEditor _R "{0}"'.format(destination) in out
    assert "_StartScriptServer" in out
    written = open(destination, encoding="utf-8").read()
    assert written == listener_source()


def test_listener_stop_when_nothing_runs(tmp_path, capsys):
    root = str(tmp_path / "site")
    run_cli(capsys, "init", "site", "--project", root)
    code, out = run_cli(capsys, "listener-stop", "--project", root)
    assert code == 0
    assert "nothing to stop" in out
