import pytest

from jig.commands import Session


@pytest.fixture
def session(tmp_path):
    return Session(str(tmp_path / "state.json"))


@pytest.fixture
def school(session):
    """A small school model exercising every feature."""
    for line in [
        "site set 180 260",
        "zone add entry 40 30 --at 0,0 --kind circulation",
        "grid set 24 --rotation 0",
        "bay add a 4x3 --spacing 24 --at 18,8",
        "wall a on --thickness 0.5",
        "aperture add a door --axis x --line 0 --offset 10 --width 3",
        "aperture add a window --axis y --line 0 --offset 30 --width 6",
        "corridor a on --axis x --line 1 --width 8",
        "cell set a 0 0 classroom-1 --label 'Classroom 1'",
        "void add a rect --at 60,36 --size 20,12",
    ]:
        session.execute(line)
    return session
