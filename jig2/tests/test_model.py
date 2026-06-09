import json
import os

import pytest

from jig.model.io import atomic_write, load_state, mint_id, save_state
from jig.model.migrate import MigrationError, migrate
from jig.model.schema import Bay, ModelError, State


def test_round_trip(tmp_path, school):
    path = str(tmp_path / "copy.json")
    save_state(school.state, path)
    loaded = load_state(path)
    assert loaded.to_dict() == school.state.to_dict()


def test_atomic_write_leaves_no_tmp(tmp_path):
    path = str(tmp_path / "out.json")
    atomic_write(path, "{}")
    assert os.path.exists(path)
    assert not os.path.exists(path + ".tmp")


def test_mint_id_never_reuses():
    assert mint_id("z", []) == "z01"
    assert mint_id("z", ["z01", "z07"]) == "z08"
    assert mint_id("ap", ["z07", "ap02"]) == "ap03"


def test_bay_spacing_length_enforced():
    with pytest.raises(ModelError):
        Bay(id="b01", name="a", counts=[3, 2], spacing_x=[24.0], spacing_y=[24.0, 24.0])


def test_bay_dimensions():
    bay = Bay(id="b01", name="a", counts=[2, 1],
              spacing_x=[24.0, 30.0], spacing_y=[20.0])
    assert bay.width == 54.0
    assert bay.depth == 20.0


def test_migrate_v3():
    v3 = {
        "schema": "plan_layout_jig_v3.0",
        "meta": {"created": "2025-01-01", "last_saved": "2025-06-01"},
        "site": {"origin": [0, 0], "width": 180.0, "height": 260.0},
        "zones": {"entry": {"corners": [[0, 0], [40, 0], [40, 30]],
                            "label": "Entry", "program_type": "circulation"}},
        "grid": {"spacing": 10.0, "rotation": 0, "origin": [0, 0]},
        "bays": {
            "A": {"grid_type": "rectangular", "origin": [18, 8],
                  "rotation_deg": 0.0, "bays": [2, 2], "spacing": [24, 24],
                  "spacing_x": None, "spacing_y": None,
                  "walls": {"enabled": True, "thickness": 0.5},
                  "corridor": {"enabled": True, "axis": "x", "position": 1,
                               "width": 8.0, "loading": "double"},
                  "apertures": [{"id": "d1", "type": "door", "axis": "x",
                                 "gridline": 0, "corner": 10.0, "width": 3.0,
                                 "hinge": "start", "swing": "positive"}],
                  "cells": {"0,0": {"name": "room1", "label": "Room 1"}}},
            "R": {"grid_type": "radial", "rings": 3},
        },
    }
    state = State.from_dict(migrate(v3))
    assert state.schema == "jig_v4"
    assert state.site.width == 180.0
    assert len(state.zones) == 1 and state.zones[0].kind == "circulation"
    assert len(state.bays) == 1  # radial bay dropped
    bay = state.bays[0]
    assert bay.spacing_x == [24.0, 24.0]
    assert bay.corridor.line == 1
    assert bay.apertures[0].swing == "in"
    assert bay.cells[0].at == [0, 0]


def test_migrate_unknown_schema_raises():
    with pytest.raises(MigrationError):
        migrate({"schema": "something_else"})


def test_load_state_migrates_v3_file(tmp_path):
    path = tmp_path / "old.json"
    path.write_text(json.dumps({
        "schema": "plan_layout_jig_v3.0",
        "site": {"origin": [0, 0], "width": 100, "height": 100},
    }))
    state = load_state(str(path))
    assert state.schema == "jig_v4"
    assert state.site.width == 100
