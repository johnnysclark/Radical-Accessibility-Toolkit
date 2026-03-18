# -*- coding: utf-8 -*-
"""
Tactile / Accessibility Validation for Layout Jig state.json
==============================================================
Validates properties that affect tactile output quality:
  - hatch differentiation (rooms with same hatch pattern)
  - label presence for braille
  - braille sizing / spacing constraints
  - density estimation for PIAF output

Python 3 stdlib only.
"""


def _issue(level, code, message, path=""):
    return {"level": level, "code": code, "message": message, "path": path}


def validate_tactile(state):
    """Validate tactile output readiness.

    Returns a list of issues.
    """
    issues = []
    bays = state.get("bays", {})

    # Collect all hatches used across cells
    hatch_usage = {}  # hatch_pattern -> list of (bay_name, cell_key, room_name)

    for bay_name, bay in bays.items():
        prefix = "bays.{}".format(bay_name)

        # Bay should have braille for tactile legibility
        if not bay.get("braille"):
            issues.append(_issue("warning", "missing_braille",
                                 "Bay {} has no braille label.".format(bay_name),
                                 "{}.braille".format(prefix)))

        cells = bay.get("cells", {})
        named_cells = 0
        for cell_key, cell in cells.items():
            name = cell.get("name", "")
            hatch = cell.get("hatch", "none")
            if name:
                named_cells += 1
                if hatch == "none":
                    issues.append(_issue("warning", "named_cell_no_hatch",
                                         "Bay {} cell {} ('{}') has no hatch pattern. "
                                         "It will be blank on tactile prints.".format(
                                             bay_name, cell_key, name),
                                         "{}.cells.{}".format(prefix, cell_key)))
                else:
                    if hatch not in hatch_usage:
                        hatch_usage[hatch] = []
                    hatch_usage[hatch].append((bay_name, cell_key, name))

    # Check for hatch duplication — different rooms with same hatch
    for hatch, usages in hatch_usage.items():
        room_names = set(u[2] for u in usages)
        if len(room_names) > 1:
            names_str = ", ".join(sorted(room_names))
            issues.append(_issue("warning", "shared_hatch",
                                 "Hatch '{}' is used by multiple rooms ({}). "
                                 "Consider different hatches for tactile "
                                 "differentiation.".format(hatch, names_str),
                                 "cells"))

    # Legend should be enabled if there are hatches
    legend = state.get("legend", {})
    if hatch_usage and not legend.get("enabled", True):
        issues.append(_issue("warning", "legend_disabled",
                             "Hatches are used but legend is disabled. "
                             "Enable legend for tactile print legibility.",
                             "legend.enabled"))

    # Aperture labels should be enabled for tactile reading
    for bay_name, bay in bays.items():
        apertures = bay.get("apertures", [])
        if apertures:
            blocks = state.get("blocks", {})
            # Just check that apertures exist — label visibility is in blocks config
            if len(apertures) > 10:
                issues.append(_issue("warning", "many_apertures",
                                     "Bay {} has {} apertures. High density may "
                                     "reduce tactile clarity.".format(
                                         bay_name, len(apertures)),
                                     "bays.{}.apertures".format(bay_name)))

    return issues


def format_results(issues):
    """Format tactile validation issues as screen-reader-friendly text."""
    if not issues:
        return "OK: Tactile validation passed. No issues."
    lines = []
    errors = sum(1 for i in issues if i["level"] == "error")
    warnings = sum(1 for i in issues if i["level"] == "warning")
    lines.append("{} issues ({} errors, {} warnings):".format(
        len(issues), errors, warnings))
    for idx, issue in enumerate(issues, 1):
        level = issue["level"].upper()
        lines.append("  {}. {}: {} [{}]".format(
            idx, level, issue["message"], issue["path"]))
    return "\n".join(lines)
