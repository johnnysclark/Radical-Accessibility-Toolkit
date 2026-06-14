# -*- coding: utf-8 -*-
"""
TEMPLATE: simple-building
=========================
A clean single-bay building, purpose-built for the accessible Rhino demo:

  * A 3-bay-by-2-bay structural grid with a perimeter of walls.
  * A front door on the south wall.
  * Three named rooms, each with a *distinct* tactile floor texture
    (ridges / waffle / bumps) so a blind reader can feel them apart.
  * The 3D tactile model enabled — walls extrude, a floor slab is added,
    and the floor carries the raised room textures.

Loaded with:  template load simple-building
Overridable:  template load simple-building bay_width=14 wall_height=10
"""

NAME = "simple-building"
DESCRIPTION = ("Single bay with perimeter walls, three rooms with distinct "
               "tactile floor textures, and the 3D tactile model on. Built "
               "for the accessible Rhino demo.")

PARAMS = [
    ("bay_width", 12.0, "Width of each structural bay, feet (3 bays across)."),
    ("bay_depth", 12.0, "Depth of each structural bay, feet (2 bays deep)."),
    ("wall_thickness", 0.5, "Wall thickness, feet."),
    ("wall_height", 9.0, "Wall height for the 3D model, feet."),
    ("cut_height", 4.0, "Section-cut height for the tactile model, feet."),
    ("door_width", 3.0, "Front door width, feet."),
]

# Cell -> (room name, tactile texture). The texture names map to floor
# patterns in the watcher: diagonal->ridges, crosshatch->waffle, dots->bumps.
_ROOM_PLAN = {
    (0, 0): ("Studio", "diagonal"),
    (0, 1): ("Studio", "diagonal"),
    (1, 0): ("Gallery", "crosshatch"),
    (1, 1): ("Gallery", "crosshatch"),
    (2, 0): ("Office", "dots"),
    (2, 1): ("Office", "dots"),
}


def build(params):
    # Imported here (not at module top) so the controller can import the
    # template manager before it has finished importing itself.
    import controller_cli as cli

    bw = float(params["bay_width"])
    bd = float(params["bay_depth"])
    wt = float(params["wall_thickness"])
    wh = float(params["wall_height"])
    ch = float(params["cut_height"])
    dw = float(params["door_width"])

    nx, ny = 3, 2
    bldg_w = nx * bw
    bldg_h = ny * bd
    margin = bw                      # one bay of open site around the building
    ox, oy = margin, margin          # building anchor
    site_w = bldg_w + 2 * margin
    site_h = bldg_h + 2 * margin

    state = cli.default_state()

    # ── Site ──
    state["site"] = {
        "origin": [0.0, 0.0], "width": site_w, "height": site_h,
        "corners": [[0.0, 0.0], [site_w, 0.0],
                    [site_w, site_h], [0.0, site_h]],
    }
    state["meta"]["notes"] = "Simple building demo (template: simple-building)"

    # ── One rectangular bay with perimeter walls + a front door ──
    door = {"id": "d1", "type": "door", "axis": "x", "gridline": 0,
            "corner": bw + (bw - dw) / 2.0, "width": dw, "height": 7.0,
            "hinge": "start", "swing": "positive"}
    bay = cli._default_bay(
        "A", (ox, oy), grid_type="rectangular", z_order=0,
        bays=(nx, ny), spacing=(bw, bd),
        walls={"enabled": True, "thickness": wt},
        apertures=[door],
        void_center=(ox + bldg_w / 2.0, oy + bldg_h / 2.0),
        void_size=(0.0, 0.0),        # no courtyard void in this building
        label="Demo Building")

    # ── Cells -> three rooms, each a distinct tactile floor texture ──
    cells = cli._init_cells(bay)
    for (c, r), (rname, texture) in _ROOM_PLAN.items():
        key = "{0},{1}".format(c, r)
        if key in cells:
            cells[key]["name"] = rname
            cells[key]["label"] = rname
            cells[key]["hatch"] = texture
    bay["cells"] = cells

    state["bays"] = {"A": bay}
    state["rooms"] = cli._auto_rooms(state["bays"])

    # ── Turn the 3D tactile model on (walls + floor + raised textures) ──
    t3 = cli._default_tactile3d()
    t3.update({"enabled": True, "wall_height": wh, "cut_height": ch,
               "floor_enabled": True, "floor_hatch_enabled": True})
    state["tactile3d"] = t3

    state["legend"]["enabled"] = True
    return state
