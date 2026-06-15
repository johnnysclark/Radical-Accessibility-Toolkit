# -*- coding: utf-8 -*-
"""
TEMPLATE: simple-building
=========================
Two test volumes that union into one L-shaped building, sharing a bent
hallway, rotated to a specific angle. Purpose-built for the accessible
Rhino demo.

Plan, before rotation (with the default 12 ft bay):

    +--------+
    | VOL B  |            Volume B — vertical wing (2 wide x 3 deep)
    | hall | G |          Volume A — horizontal wing (4 wide x 2 deep)
    +----+---+--------+   They abut along the seam and the shared wall is
    | hallway ....... |   opened where the hallway crosses, so the two
    | Studio | Office |   volumes read as one L footprint.
    +-----------------+

The whole L is then rotated by `rotation` degrees about its own center, so
the building sits at a specific angle on the site (set rotation=0 for an
axis-aligned plan).

The bent hallway runs east-west across Volume A's upper row, then turns
90 degrees and runs north up Volume B's left column. Every space — the
three rooms and the hallway — carries a distinct 2D surface texture so a
blind reader can feel them apart on the tactile plan:

    Studio  = diagonal ridges      Gallery = crosshatch (waffle)
    Office  = dots                 Hallway = horizontal lines

The 3D tactile model is on (walls extrude, floor slab), but the raised
floor textures are OFF for now — textures live on the 2D surfaces.

Loaded with:  template load simple-building
Overridable:  template load simple-building rotation=20 bay_size=14
"""
import math

NAME = "simple-building"
DESCRIPTION = ("Two volumes that union into one L-shaped building sharing a "
               "bent hallway, set at a specific angle. Three rooms plus the "
               "hallway each carry a distinct 2D floor texture. Built for the "
               "accessible Rhino demo.")

PARAMS = [
    ("bay_size", 12.0, "Size of each square structural bay, feet."),
    ("rotation", 30.0, "Angle of the whole L building, degrees (0 = axis-aligned)."),
    ("wall_thickness", 0.5, "Wall thickness, feet."),
    ("wall_height", 9.0, "Wall height for the 3D model, feet."),
    ("cut_height", 4.0, "Section-cut height for the 3D model, feet."),
    ("door_width", 3.0, "Interior door width, feet."),
]


def _rot_about(pt, pivot, deg):
    """Rotate a point about a pivot by deg degrees (CCW)."""
    rad = math.radians(deg)
    dx = pt[0] - pivot[0]
    dy = pt[1] - pivot[1]
    return (pivot[0] + dx * math.cos(rad) - dy * math.sin(rad),
            pivot[1] + dx * math.sin(rad) + dy * math.cos(rad))


def _name_cells(cells, plan):
    """Apply a {(col,row): (room_name, texture)} plan onto a cells dict."""
    for (c, r), (room_name, texture) in plan.items():
        key = "{0},{1}".format(c, r)
        if key in cells:
            cells[key]["name"] = room_name
            cells[key]["label"] = room_name
            cells[key]["hatch"] = texture


def build(params):
    # Imported here (not at module top) so the controller can import the
    # template manager before it has finished importing itself.
    import controller_cli as cli

    bs = float(params["bay_size"])
    theta = float(params["rotation"])
    wt = float(params["wall_thickness"])
    wh = float(params["wall_height"])
    ch = float(params["cut_height"])
    dw = float(params["door_width"])

    # ── Place and angle the assembly ──
    # A square site centered on the building, big enough to hold the L at any
    # rotation (the L fits inside a circle of radius ~3.2*bs about its center).
    site_side = 8.0 * bs
    pivot = (site_side / 2.0, site_side / 2.0)
    # Unrotated layout, centered on the pivot. Building bbox is 4bs wide by
    # 5bs tall, so its center sits at +(2bs, 2.5bs) from the lower-left anchor.
    anchor = (pivot[0] - 2.0 * bs, pivot[1] - 2.5 * bs)
    a_origin0 = (anchor[0], anchor[1])               # Volume A lower-left
    b_origin0 = (anchor[0], anchor[1] + 2.0 * bs)    # Volume B sits on A's left
    # Rotate each volume's origin about the shared pivot; the per-bay
    # rotation_deg then spins each volume's local geometry by the same angle,
    # so the L, the seam, and the bent hallway all stay aligned.
    a_origin = _rot_about(a_origin0, pivot, theta)
    b_origin = _rot_about(b_origin0, pivot, theta)

    state = cli.default_state()
    state["site"] = {
        "origin": [0.0, 0.0], "width": site_side, "height": site_side,
        "corners": [[0.0, 0.0], [site_side, 0.0],
                    [site_side, site_side], [0.0, site_side]],
    }
    state["meta"]["notes"] = (
        "Two-volume L demo with bent hallway at {0:.0f} degrees "
        "(template: simple-building)".format(theta))

    # ── Volume A — horizontal wing, 4 bays wide x 2 deep ──
    # Apertures: front door, the opened shared seam (portal where the hallway
    # crosses up into Volume B), and a door from each room onto the hallway.
    ap_a = [
        {"id": "d_front", "type": "door", "axis": "x", "gridline": 0,
         "corner": 2.5 * bs, "width": dw, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "seam_a", "type": "portal", "axis": "x", "gridline": 2,
         "corner": 0.0, "width": bs, "height": wh,
         "hinge": "start", "swing": "positive"},
        {"id": "studio_door", "type": "door", "axis": "x", "gridline": 1,
         "corner": 0.5 * bs, "width": dw, "height": 7.0,
         "hinge": "start", "swing": "positive"},
        {"id": "office_door", "type": "door", "axis": "x", "gridline": 1,
         "corner": 2.5 * bs, "width": dw, "height": 7.0,
         "hinge": "start", "swing": "positive"},
    ]
    bay_a = cli._default_bay(
        "A", a_origin, grid_type="rectangular", z_order=0, rotation=theta,
        bays=(4, 2), spacing=(bs, bs),
        walls={"enabled": True, "thickness": wt},
        apertures=ap_a,
        void_center=_rot_about((a_origin0[0] + 2 * bs, a_origin0[1] + bs),
                               pivot, theta),
        void_size=(0.0, 0.0),
        label="Volume A")
    cells_a = cli._init_cells(bay_a)
    _name_cells(cells_a, {
        (0, 0): ("Studio", "diagonal"), (1, 0): ("Studio", "diagonal"),
        (2, 0): ("Office", "dots"),     (3, 0): ("Office", "dots"),
        (0, 1): ("Hallway", "horizontal"), (1, 1): ("Hallway", "horizontal"),
        (2, 1): ("Hallway", "horizontal"), (3, 1): ("Hallway", "horizontal"),
    })
    bay_a["cells"] = cells_a

    # ── Volume B — vertical wing, 2 bays wide x 3 deep ──
    # Apertures: the opened shared seam (matches seam_a) and a door from the
    # Gallery onto the hallway.
    ap_b = [
        {"id": "seam_b", "type": "portal", "axis": "x", "gridline": 0,
         "corner": 0.0, "width": bs, "height": wh,
         "hinge": "start", "swing": "positive"},
        {"id": "gallery_door", "type": "door", "axis": "y", "gridline": 1,
         "corner": bs, "width": dw, "height": 7.0,
         "hinge": "start", "swing": "positive"},
    ]
    bay_b = cli._default_bay(
        "B", b_origin, grid_type="rectangular", z_order=0, rotation=theta,
        bays=(2, 3), spacing=(bs, bs),
        walls={"enabled": True, "thickness": wt},
        apertures=ap_b,
        void_center=_rot_about((b_origin0[0] + bs, b_origin0[1] + 1.5 * bs),
                               pivot, theta),
        void_size=(0.0, 0.0),
        label="Volume B")
    cells_b = cli._init_cells(bay_b)
    _name_cells(cells_b, {
        (0, 0): ("Hallway", "horizontal"), (0, 1): ("Hallway", "horizontal"),
        (0, 2): ("Hallway", "horizontal"),
        (1, 0): ("Gallery", "crosshatch"), (1, 1): ("Gallery", "crosshatch"),
        (1, 2): ("Gallery", "crosshatch"),
    })
    bay_b["cells"] = cells_b

    state["bays"] = {"A": bay_a, "B": bay_b}
    state["rooms"] = cli._auto_rooms(state["bays"])

    # ── 3D: simple walls only. Floor textures stay in 2D for now. ──
    t3 = cli._default_tactile3d()
    t3.update({"enabled": True, "wall_height": wh, "cut_height": ch,
               "floor_enabled": True, "floor_hatch_enabled": False})
    state["tactile3d"] = t3

    state["legend"]["enabled"] = True
    return state
