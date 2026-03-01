# -*- coding: utf-8 -*-
"""
Simple Corridor Test Controller
================================
One bay, 50'x50', six rooms per side of a double-loaded corridor,
one circular void (dia 20') placed at random.

Wraps the full controller_cli engine with a minimal default state.

Usage
-----
  python simple_corridor_controller.py
  python simple_corridor_controller.py --state "path/to/state.json"
"""

import random
import controller_cli as engine

# ── simple default state ───────────────────────────────────

def default_state():
    """Single bay, double-loaded corridor, random circular void."""

    # Random void centre — keep 10' clear of every edge (radius = 10')
    vx = round(random.uniform(10, 40), 1)
    vy = round(random.uniform(10, 40), 1)

    corridor = {
        "enabled": True, "axis": "x", "position": 1,
        "width": 8.0, "loading": "double",
        "hatch": "none", "hatch_scale": 4.0,
    }
    walls = {"enabled": True, "thickness": 0.5}

    bay_a = engine._default_bay(
        "A", (0, 0),
        grid_type="rectangular", z_order=0,
        bays=(6, 2), spacing=(50.0 / 6, 25.0),
        corridor=corridor, walls=walls,
        void_center=(vx, vy), void_size=(20, 20),
        void_shape="circle", label="Bay A",
    )

    bays_dict = {"A": bay_a}

    return {
        "schema": engine.SCHEMA,
        "meta": {
            "created": engine._now(),
            "last_saved": engine._now(),
            "notes": "Simple corridor test — 6+6 rooms, circular void",
        },
        "site": {"origin": [0.0, 0.0], "width": 50.0, "height": 50.0},
        "style": {
            "column_size": 1.5,
            "heavy_lineweight_mm": 1.40,
            "light_lineweight_mm": 0.08,
            "corridor_lineweight_mm": 0.35,
            "wall_lineweight_mm": 0.25,
            "label_text_height": 0.3,
            "braille_text_height": 0.5,
            "corridor_dash_len": 3.0,
            "corridor_gap_len": 2.0,
            "background_pad": 2.0,
            "label_offset": 3.0,
            "arc_segments": 16,
        },
        "bays": bays_dict,
        "blocks": engine._default_blocks(),
        "rooms": engine._auto_rooms(bays_dict),
        "legend": engine._default_legend(),
        "tactile3d": engine._default_tactile3d(),
        "hatch_library_path": "./hatches/",
        "print": engine._default_print(),
        "bambu": engine._default_bambu(),
    }


# ── patch the engine so load_state / main use our default ──
engine.default_state = default_state

if __name__ == "__main__":
    engine.main()
