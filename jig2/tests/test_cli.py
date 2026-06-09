"""CLI output contract: OK:/ERROR: prefixes, READY: sentinel, exit codes."""

import subprocess
import sys


def run_cli(tmp_path, *words):
    return subprocess.run(
        [sys.executable, "-m", "jig.cli", "--state", str(tmp_path / "state.json")]
        + list(words),
        capture_output=True, text=True)


def test_single_command(tmp_path):
    result = run_cli(tmp_path, "site", "set", "180", "260")
    assert result.returncode == 0
    lines = result.stdout.strip().split("\n")
    assert lines[0] == "OK: site set to 180 by 260 feet"
    assert lines[-1] == "READY:"


def test_error_prefix_and_exit_code(tmp_path):
    result = run_cli(tmp_path, "bogus")
    assert result.returncode == 1
    assert result.stdout.startswith("ERROR: unknown command")


def test_run_batch(tmp_path):
    result = run_cli(tmp_path, "run",
                     "site set 100 100; bay add a 2x2 --spacing 24; status")
    assert result.returncode == 0
    assert result.stdout.startswith("OK: site set")
    assert "bay a added" in result.stdout


def test_repl(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "jig.cli", "--state", str(tmp_path / "state.json"),
         "repl"],
        input="site set 80 90\nstatus\nquit\n",
        capture_output=True, text=True)
    assert result.returncode == 0
    assert "OK: site set to 80 by 90 feet" in result.stdout
    assert "OK: goodbye" in result.stdout
    assert result.stdout.count("READY:") >= 3


def test_no_decorative_output(tmp_path):
    result = run_cli(tmp_path, "site", "set", "100", "100")
    for banned in ("|", "===", "---", "─", "│", "\x1b["):
        assert banned not in result.stdout
