"""Output contract: OK:/ERROR:/READY: prefixes, speakable lines,
no tables, no box-drawing characters, line caps respected."""

import pytest

from maquette import cli, describe

BANNED_CHARACTERS = set("│┌┐└┘├┤─━║╔╗╚╝█▓▒░")


def run_cli(capsys, *args):
    code = cli.main(list(args))
    captured = capsys.readouterr()
    return code, captured.out + captured.err


@pytest.fixture
def proj_dir(tmp_path, capsys):
    root = str(tmp_path / "site")
    code, _ = run_cli(capsys, "init", "site", "--project", root)
    assert code == 0
    return root


def test_init_speaks_and_readies(tmp_path, capsys):
    code, out = run_cli(capsys, "init", "demo", "--project",
                        str(tmp_path / "demo"))
    assert code == 0
    assert out.startswith("OK: created project demo")
    assert out.rstrip().endswith("READY:")


def test_create_describe_round_trip(proj_dir, capsys):
    code, out = run_cli(capsys, "box", "10", "10", "30", "name", "tower base",
                        "--project", proj_dir, "--backend", "record")
    assert code == 0
    assert 'OK: created m1 "tower base" (box), 10 by 10 by 30' in out

    code, out = run_cli(capsys, "describe", "tower base", "--project", proj_dir)
    assert code == 0
    assert "kind: box." in out
    assert "size: 10 wide, 10 deep, 30 tall." in out

    # The spoken filler word works too: describe object "tower base".
    code, out = run_cli(capsys, "describe", "object", "tower base",
                        "--project", proj_dir)
    assert code == 0
    assert "kind: box." in out


def test_error_lines_start_with_error(proj_dir, capsys):
    code, out = run_cli(capsys, "describe", "nothing here", "--project", proj_dir)
    assert code == 1
    assert out.startswith("ERROR: ")
    assert out.rstrip().endswith("READY:")

    code, out = run_cli(capsys, "box", "10", "--project", proj_dir)
    assert code == 1
    assert "usage: box" in out


def test_every_line_short_and_clean(proj_dir, capsys):
    run_cli(capsys, "box", "10", "10", "30", "--project", proj_dir,
            "--backend", "record")
    run_cli(capsys, "sphere", "radius", "4", "at", "20,0,0",
            "--project", proj_dir, "--backend", "record")
    for args in (("describe",), ("journal",), ("help",), ("commands",)):
        code, out = run_cli(capsys, *args, "--project", proj_dir, "--all")
        assert code == 0
        for line in out.splitlines():
            assert not BANNED_CHARACTERS & set(line), line
            assert len(line) <= 100, line


def test_no_command_prints_help(capsys):
    code, out = run_cli(capsys)
    assert code == 0
    assert out.startswith("OK: Maquette")


def test_json_flag_supplements_output(proj_dir, capsys):
    code, out = run_cli(capsys, "box", "1", "1", "1", "--project", proj_dir,
                        "--backend", "record", "--json")
    assert code == 0
    lines = out.rstrip().splitlines()
    assert lines[-1] == "READY:"
    import json
    payload = json.loads(lines[-2])
    assert payload["ok"] is True


def test_measure_between_objects(proj_dir, capsys):
    run_cli(capsys, "box", "10", "10", "10", "--project", proj_dir,
            "--backend", "record")
    run_cli(capsys, "box", "10", "10", "10", "at", "30,0,0",
            "--project", proj_dir, "--backend", "record")
    code, out = run_cli(capsys, "measure", "m1", "m2", "--project", proj_dir)
    assert code == 0
    assert "distance: 30." in out
    assert "x change: 30." in out


def test_journal_search(proj_dir, capsys):
    run_cli(capsys, "box", "1", "1", "1", "--project", proj_dir,
            "--backend", "record")
    run_cli(capsys, "sphere", "radius", "2", "--project", proj_dir,
            "--backend", "record")
    code, out = run_cli(capsys, "journal", "--search", "sphere",
                        "--project", proj_dir)
    assert code == 0
    assert "create_sphere" in out
    assert "create_box" not in out


def test_describe_brief_mentions_pending(engine, capsys):
    engine.run_text("box 1 1 1")
    engine.run_text("box 1 1 1 at 0.5,0,0")
    engine.run_text("union m1 m2")
    lines = describe.brief(engine.scene())
    assert any("pending live rebuild" in line for line in lines)


def test_paging_caps_output(capsys):
    from maquette import say
    lines = ["line {0}".format(i) for i in range(40)]
    printed = say.page(lines)
    out = capsys.readouterr().out
    assert len(printed) == say.PAGE_LIMIT - 2
    assert "MORE: 22 more lines." in out
