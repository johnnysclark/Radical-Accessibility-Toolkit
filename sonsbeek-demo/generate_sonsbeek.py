#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sonsbeek Pavilion — 3D Geometry Generator
==========================================
Generates a JSON geometry file for Aldo van Eyck's 1966 Sonsbeek Pavilion
based on the original 1:100 plan drawing (Feb 19, 1966).

The pavilion consists of:
- 6 parallel north-south masonry walls (B5 blocks, 0.20 m thick, ~2.87 m tall)
- 6 semicircular curved wall segments connecting inner wall pairs
- 4 circular concrete disc elements (bench height)
- Bench-height rectangular elements at the edges and between walls
- A circular ground plane (~9 m radius) on a rectangular platform

Black lines in the plan = full-height walls (2.87 m).
Grey shapes in the plan = bench-height elements (0.90 m).

All coordinates are in meters. Origin at circle center.
X = east-west (wall spacing direction).
Y = north-south (wall length direction, positive = north).

Usage:
    python generate_sonsbeek.py              # writes sonsbeek.json
    python generate_sonsbeek.py --pretty     # 2-space indent
    python generate_sonsbeek.py --out FILE   # custom output path

No external dependencies — stdlib only.
"""
import json
import os
import sys


def build_pavilion():
    """Build the complete Sonsbeek Pavilion geometry."""

    WALL_THICKNESS = 0.20   # B5 concrete block walls
    WALL_HEIGHT = 2.87      # from section drawings
    BENCH_HEIGHT = 0.90     # grey shapes in plan
    BENCH_THICKNESS = 0.80  # wider than walls
    CIRCLE_RADIUS = 9.0     # inscribed circle

    # ------------------------------------------------------------------
    # Straight walls — 6 parallel walls running north-south (BLACK in plan)
    # These are the full-height masonry walls.
    # Far left and far right elements are bench-height (see benches below).
    # Walls numbered W2-W7 (inner 6 walls).
    # W2, W4, W5, W7 have portal gaps.
    # ------------------------------------------------------------------
    walls = [
        {
            "id": "W2",
            "label": "Wall axis 2 (outer left)",
            "x": -4.2,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -5.5, "y_end": -0.5},
                {"y_start": 0.8, "y_end": 6.0}
            ]
        },
        {
            "id": "W3",
            "label": "Inner left continuous",
            "x": -2.5,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -7.0, "y_end": 5.5}
            ]
        },
        {
            "id": "W4",
            "label": "Wall axis 1 (center-left)",
            "x": -0.8,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -5.5, "y_end": -1.5},
                {"y_start": -0.2, "y_end": 7.5}
            ]
        },
        {
            "id": "W5",
            "label": "Wall axis 6 (center-right)",
            "x": 0.8,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -7.5, "y_end": 0.2},
                {"y_start": 1.5, "y_end": 5.5}
            ]
        },
        {
            "id": "W6",
            "label": "Inner right continuous",
            "x": 2.5,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -5.5, "y_end": 7.0}
            ]
        },
        {
            "id": "W7",
            "label": "Wall axis 5 (outer right)",
            "x": 4.2,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -6.0, "y_end": -0.8},
                {"y_start": 0.5, "y_end": 5.5}
            ]
        },
    ]

    # ------------------------------------------------------------------
    # Curved walls — semicircular arcs between inner wall pairs (BLACK)
    # Full-height elements. Each spans from one wall to the adjacent wall.
    # Alternating opening directions create a serpentine path.
    #
    # Angle convention (plan view):
    #   0 deg = east (+X), 90 deg = north (+Y)
    #   start=0, end=180  -> arc curves northward, opening faces south
    #   start=180, end=360 -> arc curves southward, opening faces north
    # ------------------------------------------------------------------
    curved_walls = [
        # Between W3 (x=-2.5) and W4 (x=-0.8), gap=1.7 m, r=0.85
        {
            "id": "CW1",
            "label": "Left-inner curve, opening south",
            "center": [-1.65, 3.0],
            "radius": 0.85,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW2",
            "label": "Left-inner curve, opening north",
            "center": [-1.65, -3.5],
            "radius": 0.85,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        # Between W4 (x=-0.8) and W5 (x=0.8), gap=1.6 m, r=0.80
        {
            "id": "CW3",
            "label": "Center curve, opening south",
            "center": [0.0, 4.0],
            "radius": 0.80,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW4",
            "label": "Center curve, opening north",
            "center": [0.0, -2.5],
            "radius": 0.80,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        # Between W5 (x=0.8) and W6 (x=2.5), gap=1.7 m, r=0.85
        {
            "id": "CW5",
            "label": "Right-inner curve, opening south",
            "center": [1.65, 2.5],
            "radius": 0.85,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW6",
            "label": "Right-inner curve, opening north",
            "center": [1.65, -4.0],
            "radius": 0.85,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
    ]

    # ------------------------------------------------------------------
    # Disc elements — circular concrete screens (GREY in plan, bench height)
    # ------------------------------------------------------------------
    discs = [
        {
            "id": "D1",
            "label": "Disc top center",
            "center": [-0.3, 7.0],
            "radius": 0.35,
            "height": BENCH_HEIGHT
        },
        {
            "id": "D2",
            "label": "Disc center-left (larger)",
            "center": [-1.5, 1.0],
            "radius": 0.80,
            "height": BENCH_HEIGHT
        },
        {
            "id": "D3",
            "label": "Disc right side",
            "center": [3.3, -2.5],
            "radius": 0.60,
            "height": BENCH_HEIGHT
        },
        {
            "id": "D4",
            "label": "Disc bottom center",
            "center": [0.3, -7.0],
            "radius": 0.35,
            "height": BENCH_HEIGHT
        },
    ]

    # ------------------------------------------------------------------
    # Benches — rectangular bench-height elements (GREY rectangles in plan)
    # These include the wide elements at far left and far right,
    # and smaller bench elements between inner walls.
    # ------------------------------------------------------------------
    benches = [
        {
            "id": "B1",
            "label": "Bench far left",
            "x": -6.0,
            "thickness": BENCH_THICKNESS,
            "height": BENCH_HEIGHT,
            "segments": [
                {"y_start": -4.0, "y_end": 4.0}
            ]
        },
        {
            "id": "B2",
            "label": "Bench far right",
            "x": 6.0,
            "thickness": BENCH_THICKNESS,
            "height": BENCH_HEIGHT,
            "segments": [
                {"y_start": -5.0, "y_end": 5.0}
            ]
        },
        {
            "id": "B3",
            "label": "Bench between W6-W7 upper",
            "x": 3.35,
            "thickness": 0.50,
            "height": BENCH_HEIGHT,
            "segments": [
                {"y_start": 1.0, "y_end": 3.5}
            ]
        },
        {
            "id": "B4",
            "label": "Bench bottom center",
            "x": 1.2,
            "thickness": 0.50,
            "height": BENCH_HEIGHT,
            "segments": [
                {"y_start": -5.5, "y_end": -4.5},
                {"y_start": -6.5, "y_end": -5.8}
            ]
        },
    ]

    model = {
        "meta": {
            "name": "Sonsbeek Pavilion",
            "architect": "Aldo van Eyck",
            "year": 1966,
            "location": "Sonsbeek Park, Arnhem, Netherlands",
            "description": (
                "Temporary exhibition pavilion. A field of parallel masonry "
                "walls with semicircular connecting segments and circular "
                "concrete disc screens, arranged within a circular ground "
                "plane. Black lines are full-height walls; grey shapes are "
                "bench-height elements."
            ),
            "units": "meters",
            "source": "1:100 plan drawing, Feb 19 1966"
        },
        "site": {
            "circle_radius": CIRCLE_RADIUS,
            "platform_width": 24.0,
            "platform_depth": 16.0
        },
        "walls": walls,
        "curved_walls": curved_walls,
        "discs": discs,
        "benches": benches,
        "low_walls": []
    }

    return model


def main():
    indent = None
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "sonsbeek.json"
    )

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--pretty":
            indent = 2
        elif args[i] == "--out" and i + 1 < len(args):
            out_path = args[i + 1]
            i += 1
        i += 1

    model = build_pavilion()
    text = json.dumps(model, indent=indent)

    tmp = out_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, out_path)

    n_walls = len(model["walls"])
    n_segs = sum(len(w["segments"]) for w in model["walls"])
    n_curves = len(model["curved_walls"])
    n_discs = len(model["discs"])
    n_benches = len(model["benches"])
    print("OK: Wrote {} ({} bytes)".format(out_path, len(text)))
    print("OK: {} walls ({} segments), {} curves, {} discs, {} benches".format(
        n_walls, n_segs, n_curves, n_discs, n_benches))
    print("READY:")


if __name__ == "__main__":
    main()
