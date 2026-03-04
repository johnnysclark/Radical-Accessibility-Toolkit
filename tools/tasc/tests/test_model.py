"""Tests for TASC data model: Site, Grid, Zone, Bay, Corridor, BayVoid, TASCModel."""

import json
import tempfile
from pathlib import Path

import pytest

from tasc_core.core.model import (
    Bay,
    BayVoid,
    Corridor,
    Grid,
    Site,
    TASCModel,
    Zone,
    clear_undo,
    pop_undo,
    push_undo,
)


class TestSite:
    def test_rectangle(self):
        site = Site.rectangle(200, 150)
        assert site.width == 200
        assert site.depth == 150
        assert site.units == "feet"

    def test_rectangle_meters(self):
        site = Site.rectangle(60, 40, units="meters")
        assert site.units == "meters"

    def test_bounds(self):
        site = Site.rectangle(200, 150)
        assert site.bounds == (0, 0, 200, 150)

    def test_area_rectangle(self):
        site = Site.rectangle(200, 150)
        assert site.area == 30000.0

    def test_area_triangle(self):
        site = Site(corners=[(0, 0), (10, 0), (5, 10)])
        assert site.area == 50.0

    def test_custom_polygon(self):
        site = Site(corners=[(0, 0), (100, 0), (100, 50), (50, 100), (0, 50)])
        assert site.width == 100
        assert site.depth == 100
        assert site.area > 0

    def test_serialization(self):
        site = Site.rectangle(200, 150, units="feet")
        d = site.to_dict()
        restored = Site.from_dict(d)
        assert restored.width == 200
        assert restored.depth == 150
        assert restored.units == "feet"


class TestGrid:
    def test_defaults(self):
        g = Grid(spacing=10)
        assert g.spacing == 10
        assert g.rotation == 0.0
        assert g.origin == (0, 0)

    def test_with_rotation(self):
        g = Grid(spacing=10, rotation=45)
        assert g.rotation == 45

    def test_serialization(self):
        g = Grid(spacing=10, rotation=30, origin=(5, 5))
        d = g.to_dict()
        restored = Grid.from_dict(d)
        assert restored.spacing == 10
        assert restored.rotation == 30
        assert restored.origin == (5, 5)


class TestZone:
    def test_rectangle(self):
        z = Zone.rectangle("living", 50, 40, at=(10, 10))
        assert z.name == "living"
        assert z.width == 50
        assert z.depth == 40
        assert z.area == 2000.0

    def test_centroid(self):
        z = Zone.rectangle("test", 50, 40, at=(10, 10))
        cx, cy = z.centroid
        assert cx == 35.0  # 10 + 50/2
        assert cy == 30.0  # 10 + 40/2

    def test_polygon_zone(self):
        z = Zone(name="lobby", corners=[(0, 0), (20, 0), (20, 15), (0, 15)])
        assert z.width == 20
        assert z.depth == 15
        assert z.area == 300.0

    def test_bounds(self):
        z = Zone.rectangle("test", 50, 40, at=(10, 20))
        assert z.bounds == (10, 20, 60, 60)

    def test_program_type(self):
        z = Zone.rectangle("kitchen", 30, 20, program_type="service")
        assert z.program_type == "service"

    def test_serialization(self):
        z = Zone.rectangle("living", 50, 40, at=(10, 10), program_type="residential")
        d = z.to_dict()
        restored = Zone.from_dict(d)
        assert restored.name == "living"
        assert restored.width == 50
        assert restored.program_type == "residential"


class TestTASCModel:
    def test_empty_model(self):
        model = TASCModel()
        assert model.site is None
        assert model.grid is None
        assert model.zones == []

    def test_add_zone(self):
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        z = Zone.rectangle("living", 50, 40, at=(10, 10))
        warnings = model.add_zone(z)
        assert len(model.zones) == 1
        assert warnings == []

    def test_add_zone_outside_boundary(self):
        model = TASCModel()
        model.site = Site.rectangle(100, 100)
        z = Zone.rectangle("big", 150, 50, at=(0, 0))
        warnings = model.add_zone(z)
        assert len(warnings) > 0

    def test_add_overlapping_zones(self):
        model = TASCModel()
        model.site = Site.rectangle(200, 200)
        z1 = Zone.rectangle("a", 50, 50, at=(10, 10))
        z2 = Zone.rectangle("b", 50, 50, at=(30, 30))
        model.add_zone(z1)
        warnings = model.add_zone(z2)
        assert len(warnings) > 0

    def test_remove_zone(self):
        model = TASCModel()
        z = Zone.rectangle("living", 50, 40)
        model.zones.append(z)
        assert model.remove_zone("living") is True
        assert len(model.zones) == 0

    def test_remove_zone_case_insensitive(self):
        model = TASCModel()
        z = Zone.rectangle("Living", 50, 40)
        model.zones.append(z)
        assert model.remove_zone("living") is True

    def test_remove_nonexistent(self):
        model = TASCModel()
        assert model.remove_zone("nothing") is False

    def test_get_zone(self):
        model = TASCModel()
        z = Zone.rectangle("kitchen", 30, 20)
        model.zones.append(z)
        found = model.get_zone("kitchen")
        assert found is not None
        assert found.name == "kitchen"

    def test_total_zone_area(self):
        model = TASCModel()
        model.zones.append(Zone.rectangle("a", 50, 40))  # 2000
        model.zones.append(Zone.rectangle("b", 30, 20))  # 600
        assert model.total_zone_area == 2600.0

    def test_serialization_roundtrip(self):
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        model.grid = Grid(spacing=10, rotation=15)
        model.zones.append(Zone.rectangle("living", 50, 40, at=(10, 10)))
        model.zones.append(Zone.rectangle("kitchen", 30, 20, at=(70, 10)))

        d = model.to_dict()
        restored = TASCModel.from_dict(d)
        assert restored.site.width == 200
        assert restored.grid.spacing == 10
        assert len(restored.zones) == 2
        assert restored.zones[0].name == "living"

    def test_save_load(self, tmp_path):
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        model.zones.append(Zone.rectangle("test", 50, 40, at=(10, 10)))

        path = tmp_path / "state.json"
        model.save(path)
        assert path.exists()

        loaded = TASCModel.load(path)
        assert loaded.site.width == 200
        assert len(loaded.zones) == 1
        assert loaded.zones[0].name == "test"


class TestZoneLabels:
    def test_zone_label_defaults(self):
        z = Zone.rectangle("living", 50, 40)
        assert z.label == ""
        assert z.braille == ""

    def test_zone_label_set(self):
        z = Zone.rectangle("living", 50, 40)
        z.label = "Living Room"
        z.braille = "⠇⠊⠧⠊⠝⠛"
        assert z.label == "Living Room"
        assert z.braille == "⠇⠊⠧⠊⠝⠛"

    def test_zone_label_serialization(self):
        z = Zone.rectangle("living", 50, 40)
        z.label = "Living Room"
        z.braille = "⠇⠊⠧⠊⠝⠛"
        d = z.to_dict()
        assert d["label"] == "Living Room"
        assert d["braille"] == "⠇⠊⠧⠊⠝⠛"
        restored = Zone.from_dict(d)
        assert restored.label == "Living Room"
        assert restored.braille == "⠇⠊⠧⠊⠝⠛"

    def test_zone_label_omitted_when_empty(self):
        z = Zone.rectangle("living", 50, 40)
        d = z.to_dict()
        assert "label" not in d
        assert "braille" not in d


class TestCorridor:
    def test_defaults(self):
        c = Corridor()
        assert c.enabled is False
        assert c.axis == "x"
        assert c.position == 1
        assert c.width == 8.0
        assert c.loading == "double"

    def test_enabled(self):
        c = Corridor(enabled=True, axis="y", width=10.0, loading="single")
        assert c.enabled is True
        assert c.axis == "y"
        assert c.width == 10.0
        assert c.loading == "single"

    def test_serialization(self):
        c = Corridor(enabled=True, axis="y", position=2, width=10.0, loading="single")
        d = c.to_dict()
        restored = Corridor.from_dict(d)
        assert restored.enabled is True
        assert restored.axis == "y"
        assert restored.position == 2
        assert restored.width == 10.0
        assert restored.loading == "single"


class TestBayVoid:
    def test_defaults(self):
        v = BayVoid()
        assert v.center == (0, 0)
        assert v.size == (20, 20)
        assert v.shape == "rectangle"

    def test_circle(self):
        v = BayVoid(center=(50, 50), size=(24, 24), shape="circle")
        assert v.shape == "circle"
        assert v.size == (24, 24)

    def test_serialization(self):
        v = BayVoid(center=(90, 44), size=(30, 18), shape="rectangle")
        d = v.to_dict()
        restored = BayVoid.from_dict(d)
        assert restored.center == (90, 44)
        assert restored.size == (30, 18)
        assert restored.shape == "rectangle"


class TestBay:
    def test_creation(self):
        bay = Bay(name="A", grid=(6, 3), spacing=(24, 24), origin=(18, 8))
        assert bay.name == "A"
        assert bay.grid == (6, 3)
        assert bay.spacing == (24, 24)
        assert bay.origin == (18, 8)

    def test_column_count(self):
        bay = Bay(name="A", grid=(6, 3))
        assert bay.column_count == 28  # (6+1) * (3+1)

    def test_column_count_1x1(self):
        bay = Bay(name="B", grid=(1, 1))
        assert bay.column_count == 4  # (1+1) * (1+1)

    def test_gridlines_regular(self):
        bay = Bay(name="A", grid=(3, 2), spacing=(24, 30))
        assert bay.gridlines_x == [0, 24, 48, 72]
        assert bay.gridlines_y == [0, 30, 60]

    def test_gridlines_irregular(self):
        bay = Bay(name="A", grid=(4, 2), spacing_x=[24, 30, 24, 18])
        gx = bay.gridlines_x
        assert gx == [0, 24, 54, 78, 96]

    def test_footprint(self):
        bay = Bay(name="A", grid=(6, 3), spacing=(24, 24))
        fp = bay.footprint
        assert fp == (144, 72)

    def test_extents_no_rotation(self):
        bay = Bay(name="A", grid=(2, 2), spacing=(10, 10), origin=(5, 5))
        ext = bay.extents
        assert ext == (5, 5, 25, 25)

    def test_extents_with_rotation(self):
        bay = Bay(name="A", grid=(1, 1), spacing=(10, 10), origin=(0, 0), rotation=90)
        min_x, min_y, max_x, max_y = bay.extents
        assert abs(min_x - (-10)) < 0.01
        assert abs(min_y - 0) < 0.01
        assert abs(max_x - 0) < 0.01
        assert abs(max_y - 10) < 0.01

    def test_defaults(self):
        bay = Bay(name="X")
        assert bay.origin == (0, 0)
        assert bay.rotation == 0.0
        assert bay.grid == (1, 1)
        assert bay.spacing == (24, 24)
        assert bay.column_size == 1.5
        assert bay.corridor is None
        assert bay.void is None
        assert bay.label == ""
        assert bay.braille == ""

    def test_with_corridor_and_void(self):
        bay = Bay(
            name="A",
            grid=(6, 3),
            corridor=Corridor(enabled=True, axis="x", width=8),
            void=BayVoid(center=(90, 44), size=(30, 18)),
        )
        assert bay.corridor.enabled is True
        assert bay.void.size == (30, 18)

    def test_serialization(self):
        bay = Bay(
            name="A",
            origin=(18, 8),
            rotation=15,
            grid=(6, 3),
            spacing=(24, 24),
            column_size=2.0,
            corridor=Corridor(enabled=True, axis="x", width=8),
            void=BayVoid(center=(90, 44), size=(30, 18)),
            label="Library",
            braille="⠇⠊⠃⠗⠁⠗⠽",
        )
        d = bay.to_dict()
        restored = Bay.from_dict(d)
        assert restored.name == "A"
        assert restored.origin == (18, 8)
        assert restored.rotation == 15
        assert restored.grid == (6, 3)
        assert restored.column_size == 2.0
        assert restored.corridor.enabled is True
        assert restored.corridor.axis == "x"
        assert restored.void.center == (90, 44)
        assert restored.label == "Library"
        assert restored.braille == "⠇⠊⠃⠗⠁⠗⠽"

    def test_serialization_minimal(self):
        bay = Bay(name="B")
        d = bay.to_dict()
        assert "corridor" not in d
        assert "void" not in d
        assert "label" not in d
        restored = Bay.from_dict(d)
        assert restored.corridor is None
        assert restored.void is None
        assert restored.label == ""

    def test_irregular_spacing_serialization(self):
        bay = Bay(name="A", grid=(4, 2), spacing_x=[24, 30, 24, 18])
        d = bay.to_dict()
        assert d["spacing_x"] == [24, 30, 24, 18]
        restored = Bay.from_dict(d)
        assert restored.spacing_x == [24, 30, 24, 18]


class TestTASCModelBays:
    def test_add_bay(self):
        model = TASCModel()
        bay = Bay(name="A", grid=(6, 3))
        model.add_bay(bay)
        assert len(model.bays) == 1

    def test_add_bay_replaces(self):
        model = TASCModel()
        model.add_bay(Bay(name="A", grid=(6, 3)))
        model.add_bay(Bay(name="A", grid=(4, 2)))
        assert len(model.bays) == 1
        assert model.bays[0].grid == (4, 2)

    def test_get_bay(self):
        model = TASCModel()
        model.add_bay(Bay(name="A", grid=(6, 3)))
        found = model.get_bay("A")
        assert found is not None
        assert found.grid == (6, 3)

    def test_get_bay_case_insensitive(self):
        model = TASCModel()
        model.add_bay(Bay(name="Alpha", grid=(6, 3)))
        assert model.get_bay("alpha") is not None

    def test_remove_bay(self):
        model = TASCModel()
        model.add_bay(Bay(name="A"))
        assert model.remove_bay("A") is True
        assert len(model.bays) == 0

    def test_remove_bay_nonexistent(self):
        model = TASCModel()
        assert model.remove_bay("Z") is False

    def test_serialization_with_bays(self):
        model = TASCModel()
        model.site = Site.rectangle(200, 150)
        model.add_bay(Bay(name="A", grid=(6, 3), spacing=(24, 24)))
        model.add_bay(Bay(name="B", grid=(3, 3)))
        d = model.to_dict()
        restored = TASCModel.from_dict(d)
        assert len(restored.bays) == 2
        assert restored.bays[0].name == "A"
        assert restored.bays[1].name == "B"


class TestUndo:
    def test_push_and_pop(self, tmp_path):
        state_path = tmp_path / ".tasc_state.json"
        model1 = TASCModel()
        model1.site = Site.rectangle(100, 100)
        push_undo(model1, state_path)

        model2 = TASCModel()
        model2.site = Site.rectangle(200, 200)
        push_undo(model2, state_path)

        restored = pop_undo(state_path)
        assert restored is not None
        assert restored.site.width == 200

        restored2 = pop_undo(state_path)
        assert restored2 is not None
        assert restored2.site.width == 100

    def test_pop_empty(self, tmp_path):
        state_path = tmp_path / ".tasc_state.json"
        assert pop_undo(state_path) is None

    def test_max_undo(self, tmp_path):
        state_path = tmp_path / ".tasc_state.json"
        for i in range(15):
            model = TASCModel()
            model.site = Site.rectangle(float(i), float(i))
            push_undo(model, state_path)

        undo_path = tmp_path / ".tasc_undo.json"
        stack = json.loads(undo_path.read_text())
        assert len(stack) == 10

    def test_clear_undo(self, tmp_path):
        state_path = tmp_path / ".tasc_state.json"
        model = TASCModel()
        push_undo(model, state_path)
        clear_undo(state_path)
        undo_path = tmp_path / ".tasc_undo.json"
        assert not undo_path.exists()

    def test_clear_undo_no_file(self, tmp_path):
        state_path = tmp_path / ".tasc_state.json"
        clear_undo(state_path)  # Should not raise
