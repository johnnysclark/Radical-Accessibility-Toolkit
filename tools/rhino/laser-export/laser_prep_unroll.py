# -*- coding: utf-8 -*-
"""
Laser Prep (Unroll) -- unroll selected 3D solids into flat cut patterns,
extract exterior borders, row-pack on the virtual sheet at a target print
scale, stage the border curves onto a laser layer.

This is the peer of laser_prep_make2d. The difference:

  - Make2D projects 3D onto a plane to produce a single 2D drawing.
    Used when the laser output is a *drawing of* the object
    (site plan, elevation, section).
  - Unroll unfolds each 3D solid into its constituent flat faces.
    Used when the laser output is *the physical object itself*:
    chipboard massing model, folded-paper study, assembly piece.

Each selected solid is duplicated, unrolled with explode=True, and the
exterior border of every resulting face is copied onto the target laser
layer. Faces inside one piece are compressed to a tight strip using a
back-computed gap (inches-in-AI -> doc-units at the user's target scale),
and pieces are then row-packed into the 40x24 bed using first-fit
decreasing. A per-piece OK or SKIPPED line is printed so the user knows
which solids didn't unroll (non-developable doubly-curved surfaces will
fail and be reported). All bottom faces are kept; the user prunes those
manually in Rhino before export if they don't want them.

Usage inside Rhino::

    import laser_prep_unroll as lpu
    lpu.unroll_and_stage("cut", scale_den=48)
    lpu.unroll_and_stage("engrave", scale_num=1, scale_den=96,
                         face_gap_inches=0.125,
                         piece_pad_inches=0.25)

IronPython 2.7 compatible.
"""

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino

import laser_setup as _ls
import laser_prep_selection as _lps


# SCD bed dimensions in inches (landscape).
_BED_W_IN = 40.0
_BED_H_IN = 24.0

# Defaults in inches-as-they-appear-in-the-final-AI.
_DEFAULT_FACE_GAP_IN = 0.25
_DEFAULT_PIECE_PAD_IN = 0.25

# Staging y-coordinate -- somewhere far from the source so intermediate
# unroll results don't collide with the original geometry or with each other.
_STAGING_Y_FT = -1.0e5


def _doc_to_inches():
    """Scale factor from current doc unit to inches (12 for feet, 1 for inches, ...)."""
    return rs.UnitScale(Rhino.UnitSystem.Inches)


def _back_compute(val_in, scale_num, scale_den, doc_to_in):
    """Convert an AI-inches target size into the equivalent doc-unit size
    at print scale 1:D.

    At 1:D, one AI inch represents D inches real-world, which is
    D / doc_to_inches doc-units. So:

        val_doc = val_in * (den / num) / doc_to_in
    """
    return float(val_in) * float(scale_den) / (float(scale_num) * float(doc_to_in))


def _strip_bbox(face_ids):
    """Return (min_x, min_y, max_x, max_y) across a list of face ids."""
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")
    for fid in face_ids:
        bb = rs.BoundingBox(fid)
        if not bb:
            continue
        if bb[0][0] < min_x: min_x = bb[0][0]
        if bb[0][1] < min_y: min_y = bb[0][1]
        if bb[6][0] > max_x: max_x = bb[6][0]
        if bb[6][1] > max_y: max_y = bb[6][1]
    return min_x, min_y, max_x, max_y


def _compress_strip(face_ids, gap_doc):
    """Lay faces in a tight strip: left to right, `gap_doc` between faces,
    all aligned to their shared row bottom. Returns a dict describing
    the strip's current bbox after the moves.
    """
    items = []
    for fid in face_ids:
        bb = rs.BoundingBox(fid)
        if not bb:
            continue
        items.append({
            "id": fid,
            "min_x": bb[0][0], "min_y": bb[0][1],
            "w": bb[6][0] - bb[0][0], "h": bb[6][1] - bb[0][1],
        })
    if not items:
        return None
    items.sort(key=lambda d: d["min_x"])
    row_min_y = min(it["min_y"] for it in items)
    cur_x = 0.0
    for it in items:
        dx = cur_x - it["min_x"]
        dy = row_min_y - it["min_y"]
        rs.MoveObject(it["id"], [dx, dy, 0])
        cur_x += it["w"] + gap_doc
    ids = [it["id"] for it in items]
    min_x, min_y, max_x, max_y = _strip_bbox(ids)
    return {"ids": ids, "min_x": min_x, "min_y": min_y,
            "w": max_x - min_x, "h": max_y - min_y}


def _row_pack(pieces, max_width_doc, pad_doc):
    """First-fit decreasing shelf pack.

    Args:
        pieces: list of {"w": width, "h": height} in doc units.
        max_width_doc: shelf width cap in doc units (the bed width at
                       the target scale).
        pad_doc: gap between pieces and between shelves.

    Returns: (placements, total_w, total_h) where placements is a list
    indexed by piece-id of (x, y) positions for each piece's lower-left
    corner, and total_w/total_h describe the packed extent.
    """
    n = len(pieces)
    sorted_idx = sorted(range(n), key=lambda i: -pieces[i]["h"])
    shelves = []   # each: {"h": shelf_height, "used": width_consumed}
    shelf_of = {}  # piece_idx -> shelf_idx
    x_in_shelf = {}
    for pi in sorted_idx:
        p = pieces[pi]
        placed = False
        for si, sh in enumerate(shelves):
            if sh["h"] >= p["h"] and sh["used"] + p["w"] + pad_doc <= max_width_doc:
                x_in_shelf[pi] = sh["used"]
                sh["used"] += p["w"] + pad_doc
                shelf_of[pi] = si
                placed = True
                break
        if not placed:
            shelves.append({"h": p["h"], "used": p["w"] + pad_doc})
            x_in_shelf[pi] = 0.0
            shelf_of[pi] = len(shelves) - 1
    shelf_ys = [0.0]
    for sh in shelves[:-1]:
        shelf_ys.append(shelf_ys[-1] + sh["h"] + pad_doc)
    placements = [None] * n
    total_w = 0.0
    for pi in range(n):
        si = shelf_of[pi]
        placements[pi] = (x_in_shelf[pi], shelf_ys[si])
        right = x_in_shelf[pi] + pieces[pi]["w"]
        if right > total_w:
            total_w = right
    total_h = shelf_ys[-1] + shelves[-1]["h"] if shelves else 0.0
    return placements, total_w, total_h


def unroll_and_stage(op, scale_num=1, scale_den=48,
                     face_gap_inches=_DEFAULT_FACE_GAP_IN,
                     piece_pad_inches=_DEFAULT_PIECE_PAD_IN):
    """Unroll selected 3D solids, row-pack, stage borders on a laser layer.

    Args:
        op: "cut", "engrave", or "vector_engrave".
        scale_num, scale_den: the scale the caller will pass to
            laser_export.export_laser_ai. Gaps are back-computed from
            inches-in-AI to doc units at this scale so they land at the
            requested spacing in the final file.
        face_gap_inches: spacing between faces within one piece, measured
            in the final AI.
        piece_pad_inches: spacing between piece rows, measured in the
            final AI.

    Returns: count of staged curves. Prints per-piece OK / SKIPPED lines
    and an overflow WARN if the packed extent exceeds the bed at scale.
    """
    op_norm = (op or "").strip().lower().replace("-", "_")
    if op_norm not in ("cut", "engrave", "vector_engrave"):
        print("ERROR: unroll_and_stage: op must be 'cut', 'engrave', or 'vector_engrave'. Got '{0}'.".format(op))
        print("READY:")
        return 0
    if int(scale_num) <= 0 or int(scale_den) <= 0:
        print("ERROR: unroll_and_stage: scale must be positive (e.g. 1:48).")
        print("READY:")
        return 0

    sel = rs.SelectedObjects() or []
    if not sel:
        print("ERROR: unroll_and_stage: no selection. Select 3D solids first.")
        print("READY:")
        return 0

    _ls.ensure_layers(draw_artboard=False)

    doc_to_in = _doc_to_inches()
    face_gap_doc = _back_compute(face_gap_inches, scale_num, scale_den, doc_to_in)
    pad_doc = _back_compute(piece_pad_inches, scale_num, scale_den, doc_to_in)
    max_w_doc = _back_compute(_BED_W_IN, scale_num, scale_den, doc_to_in)
    max_h_doc = _back_compute(_BED_H_IN, scale_num, scale_den, doc_to_in)

    rs.EnableRedraw(False)
    pieces = []  # list of dicts with "ids", "w", "h", "min_x", "min_y"
    staging_y = _STAGING_Y_FT

    for i, sid in enumerate(sel):
        # Duplicate the source far aside so the unroll's working copy
        # doesn't interfere with the user's viewport focus.
        dup = rs.CopyObject(sid, [max_w_doc * 3.0, 0, 0])
        if not dup:
            print("SKIPPED: piece {0} duplicate failed.".format(i))
            continue
        try:
            unrolled = rs.UnrollSurface(dup, explode=True)
        except Exception as e:
            print("SKIPPED: piece {0} unroll raised: {1}".format(i, e))
            rs.DeleteObject(dup)
            continue
        rs.DeleteObject(dup)
        if not unrolled:
            print("SKIPPED: piece {0} unroll produced no faces (non-developable surface?).".format(i))
            continue
        strip = _compress_strip(unrolled, face_gap_doc)
        if not strip:
            print("SKIPPED: piece {0} strip measurement failed.".format(i))
            continue
        # Park the piece at the staging y far below origin so subsequent
        # unrolls don't land on top of it.
        dx = 0.0 - strip["min_x"]
        dy = staging_y - strip["min_y"]
        rs.MoveObjects(strip["ids"], [dx, dy, 0])
        strip["min_x"] = 0.0
        strip["min_y"] = staging_y
        staging_y += strip["h"] + pad_doc
        pieces.append(strip)
        print("OK: piece {0} unrolled, {1} face(s), {2:.2f} x {3:.2f} doc-units.".format(
            i, len(strip["ids"]), strip["w"], strip["h"]))

    if not pieces:
        print("ERROR: unroll_and_stage: no pieces unrolled successfully.")
        print("READY:")
        rs.EnableRedraw(True)
        return 0

    # Row-pack into the scaled bed footprint, then move each piece from
    # its staging y to its packed position.
    placements, total_w, total_h = _row_pack(pieces, max_w_doc, pad_doc)
    for pi, (tx, ty) in enumerate(placements):
        dx = tx - pieces[pi]["min_x"]
        dy = ty - pieces[pi]["min_y"]
        rs.MoveObjects(pieces[pi]["ids"], [dx, dy, 0])

    if total_w > max_w_doc * 1.001:
        print("WARN: packed width {0:.2f} exceeds bed width {1:.2f} at 1:{2}. Use a larger denominator.".format(
            total_w, max_w_doc, int(scale_den / scale_num)))
    if total_h > max_h_doc * 1.001:
        print("WARN: packed height {0:.2f} exceeds bed height {1:.2f} at 1:{2}. Use a larger denominator.".format(
            total_h, max_h_doc, int(scale_den / scale_num)))

    # Extract exterior borders as curves and stage them.
    all_face_ids = []
    for p in pieces:
        all_face_ids.extend(p["ids"])

    borders = []
    for fid in all_face_ids:
        try:
            b = rs.DuplicateSurfaceBorder(fid, type=1)
        except Exception as e:
            print("WARN: border extraction failed on a face: {0}".format(e))
            continue
        if b:
            borders.extend(b)

    # Drop the flat surfaces -- the curves are the cut deliverable.
    if all_face_ids:
        rs.DeleteObjects(all_face_ids)

    if not borders:
        print("ERROR: unroll_and_stage: no borders extracted. Nothing staged.")
        print("READY:")
        rs.EnableRedraw(True)
        return 0

    rs.UnselectAllObjects()
    rs.SelectObjects(borders)
    rs.EnableRedraw(True)
    return _lps.stage(op_norm)


if __name__ == "__main__":
    choice = rs.GetString("Laser op (after unroll)", "cut", ["cut", "engrave", "vector_engrave"])
    den = rs.GetInteger("Scale 1:D -- enter D", 48, 1, 10000)
    if choice and den:
        unroll_and_stage(choice, scale_num=1, scale_den=den)
