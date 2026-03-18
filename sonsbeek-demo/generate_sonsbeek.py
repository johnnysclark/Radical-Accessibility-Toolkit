#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sonsbeek Pavilion — 3D Geometry Generator
==========================================
Generates a JSON geometry file for Aldo van Eyck's 1966 Sonsbeek Pavilion
based on the original 1:100 plan drawing (Feb 19, 1966).

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
    PLINTH_HEIGHT = 0.20    # visible raised platform

    # ------------------------------------------------------------------
    # Wall spacing: inner pairs are 2.0 m apart (for r=1.0 curves),
    # outer pairs are 1.5 m apart. Total field = 12 m (x=-6 to x=6).
    #
    #   B1(-6) -- 1.5 -- W2(-4.5) -- 1.5 -- W3(-3.0)
    #          -- 2.0 -- W4(-1.0) -- 2.0 -- W5(1.0)
    #          -- 2.0 -- W6(3.0) -- 1.5 -- W7(4.5) -- 1.5 -- B2(6)
    # ------------------------------------------------------------------
    walls = [
        {
            "id": "W2",
            "label": "Outer left (gap at center)",
            "x": -4.5,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -5.5, "y_end": -0.5},
                {"y_start": 0.8, "y_end": 6.0}
            ]
        },
        {
            "id": "W3",
            "label": "Inner left (continuous)",
            "x": -3.0,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -7.0, "y_end": 5.5}
            ]
        },
        {
            "id": "W4",
            "label": "Center-left (gap at center)",
            "x": -1.0,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -6.0, "y_end": -1.5},
                {"y_start": -0.2, "y_end": 7.5}
            ]
        },
        {
            "id": "W5",
            "label": "Center-right (gap at center)",
            "x": 1.0,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -7.5, "y_end": 0.2},
                {"y_start": 1.5, "y_end": 5.5}
            ]
        },
        {
            "id": "W6",
            "label": "Inner right (continuous)",
            "x": 3.0,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -6.0, "y_end": 7.0}
            ]
        },
        {
            "id": "W7",
            "label": "Outer right (gap at center)",
            "x": 4.5,
            "thickness": WALL_THICKNESS,
            "height": WALL_HEIGHT,
            "segments": [
                {"y_start": -6.0, "y_end": -0.5},
                {"y_start": 0.5, "y_end": 5.5}
            ]
        },
    ]

    # ------------------------------------------------------------------
    # Curved walls — semicircular arcs between inner wall pairs (BLACK)
    # Inner pairs are 2.0 m apart → radius = 1.0 m.
    #
    # Angle convention (plan view):
    #   0 deg = east (+X), 90 deg = north (+Y)
    #   start=0, end=180  → arc curves northward, opening faces south
    #   start=180, end=360 → arc curves southward, opening faces north
    # ------------------------------------------------------------------
    curved_walls = [
        # Between W3 (x=-3.0) and W4 (x=-1.0), gap=2.0 m, r=1.0
        {
            "id": "CW1",
            "label": "Left curve, opening south",
            "center": [-2.0, 3.0],
            "radius": 1.0,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW2",
            "label": "Left curve, opening north",
            "center": [-2.0, -3.0],
            "radius": 1.0,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        # Between W4 (x=-1.0) and W5 (x=1.0), gap=2.0 m, r=1.0
        {
            "id": "CW3",
            "label": "Center curve, opening south",
            "center": [0.0, 3.5],
            "radius": 1.0,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW4",
            "label": "Center curve, opening north",
            "center": [0.0, -2.5],
            "radius": 1.0,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        # Between W5 (x=1.0) and W6 (x=3.0), gap=2.0 m, r=1.0
        {
            "id": "CW5",
            "label": "Right curve, opening south",
            "center": [2.0, 2.5],
            "radius": 1.0,
            "start_angle_deg": 0,
            "end_angle_deg": 180,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
        {
            "id": "CW6",
            "label": "Right curve, opening north",
            "center": [2.0, -3.5],
            "radius": 1.0,
            "start_angle_deg": 180,
            "end_angle_deg": 360,
            "height": WALL_HEIGHT,
            "thickness": WALL_THICKNESS
        },
    ]

    # ------------------------------------------------------------------
    # Disc elements — circular concrete screens (GREY in plan)
    # ------------------------------------------------------------------
    discs = [
        {
            "id": "D1",
            "label": "Disc top center",
            "center": [-0.3, 7.0],
            "radius": 0.35,
            "height": 1.5
        },
        {
            "id": "D2",
            "label": "Disc center-left (larger)",
            "center": [-1.5, 0.5],
            "radius": 0.80,
            "height": 2.0
        },
        {
            "id": "D3",
            "label": "Disc right side",
            "center": [3.75, -2.5],
            "radius": 0.60,
            "height": 2.0
        },
        {
            "id": "D4",
            "label": "Disc bottom center",
            "center": [0.3, -7.0],
            "radius": 0.35,
            "height": 1.5
        },
    ]

    # ------------------------------------------------------------------
    # Benches — rectangular bench-height elements (GREY rectangles)
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
            "label": "Bench between W6-W7",
            "x": 3.75,
            "thickness": 0.50,
            "height": BENCH_HEIGHT,
            "segments": [
                {"y_start": 1.0, "y_end": 3.5}
            ]
        },
        {
            "id": "B4",
            "label": "Bench bottom center",
            "x": 1.5,
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
            "plinth_height": PLINTH_HEIGHT,
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
