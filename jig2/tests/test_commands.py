import pytest

from jig.commands import CommandError, Session
from jig.describe import describe, status


def test_site_set(session):
    message = session.execute("site set 180 260")
    assert message == "site set to 180 by 260 feet"
    assert session.state.site.width == 180.0


def test_unknown_command(session):
    with pytest.raises(CommandError) as err:
        session.execute("frobnicate")
    assert "unknown command" in str(err.value)


def test_bay_add_and_list(session):
    message = session.execute("bay add a 6x4 --spacing 24 --at 18,8")
    assert "bay a added" in message
    assert "35 columns" in message
    listing = session.execute("bay list")
    assert "bay a: 6 by 4 bays at 18,8" in listing


def test_bay_irregular_spacing(session):
    session.execute("bay add a 3x2 --spacing-x 24,30,24 --spacing-y 20")
    bay = session.state.find_bay("a")
    assert bay.spacing_x == [24.0, 30.0, 24.0]
    assert bay.spacing_y == [20.0, 20.0]


def test_duplicate_bay_rejected(session):
    session.execute("bay add a 2x2 --spacing 24")
    with pytest.raises(CommandError):
        session.execute("bay add a 2x2 --spacing 24")


def test_failed_mutation_rolls_back(session):
    session.execute("bay add a 2x2 --spacing 24")
    before = session.state.to_dict()
    with pytest.raises(CommandError):
        # valid bay, but aperture offset beyond the wall: must not half-apply
        session.execute("aperture add a door --axis x --line 0 --offset 100 --width 3")
    assert session.state.to_dict() == before


def test_undo(session):
    session.execute("site set 100 100")
    session.execute("bay add a 2x2 --spacing 24")
    assert session.execute("undo") == "undid 1 change"
    assert session.state.bays == []
    assert session.state.site.width == 100.0


def test_undo_empty(session):
    with pytest.raises(CommandError):
        session.execute("undo")


def test_snapshot_save_load(session):
    session.execute("site set 100 100")
    session.execute("snapshot save before-bays")
    session.execute("bay add a 2x2 --spacing 24")
    session.execute("snapshot load before-bays")
    assert session.state.bays == []
    assert "before-bays" in session.execute("snapshot list")


def test_snapshot_diff(session):
    session.execute("site set 100 100")
    session.execute("snapshot save base")
    session.execute("bay add a 2x2 --spacing 24")
    diff = session.execute("snapshot diff base")
    assert "differences" in diff


def test_run_script_atomic(session):
    with pytest.raises(CommandError):
        session.run_script([
            "site set 100 100",
            "bay add a 2x2 --spacing 24",
            "bogus command here",
        ])
    assert session.state.site.boundary == []
    assert session.state.bays == []


def test_run_script_single_undo_frame(session):
    session.run_script(["site set 100 100", "bay add a 2x2 --spacing 24"])
    session.execute("undo")
    assert session.state.site.boundary == []


def test_state_persists_across_sessions(tmp_path):
    path = str(tmp_path / "state.json")
    first = Session(path)
    first.execute("site set 50 60")
    second = Session(path)
    assert second.state.site.depth == 60.0


def test_corridor_validation(session):
    session.execute("bay add a 2x2 --spacing 24")
    with pytest.raises(CommandError):
        session.execute("corridor a on --axis x --line 2 --width 8")
    session.execute("corridor a on --axis x --line 1 --width 8")
    assert session.state.find_bay("a").corridor.width == 8.0


def test_cell_set_and_clear(session):
    session.execute("bay add a 2x2 --spacing 24")
    session.execute("cell set a 0 1 office --label Office")
    assert "office" in session.execute("cell list a")
    session.execute("cell clear a 0 1")
    assert session.execute("cell list a") == "bay a has no named cells"


def test_zone_polygon(session):
    session.execute("zone polygon yard 0,0 50,0 50,40 25,60 0,40 --kind open")
    zone = session.state.find_zone("yard")
    assert len(zone.boundary) == 5
    assert zone.kind == "open"


def test_measure(school):
    message = school.execute("measure a entry")
    assert message.startswith("distance from a to entry is")
    cell_distance = school.execute("measure a/0,0 a/3,2")
    assert "distance" in cell_distance


def test_validate_clean(school):
    assert school.execute("validate") == "model is clean, no findings"


def test_validate_finds_problems(session):
    session.execute("site set 50 50")
    session.execute("bay add a 4x4 --spacing 24")  # 96x96 bay outside 50x50 site
    findings = session.execute("validate")
    assert "outside the site" in findings


def test_help(session):
    listing = session.execute("help")
    assert "bay add" in listing
    detail = session.execute("help bay add")
    assert "NxM" in detail


def test_describe_and_status(school):
    prose = describe(school.state)
    for fragment in ("site: 4 corners", "bay a", "corridor: axis x",
                     "door ap01", "cell 0,0: classroom-1"):
        assert fragment in prose, fragment
    line = status(school.state)
    assert "1 bays" in line and "site set" in line


def test_describe_section(school):
    assert describe(school.state, "site").startswith("site:")
    assert "unknown section" in describe(school.state, "nonsense")
