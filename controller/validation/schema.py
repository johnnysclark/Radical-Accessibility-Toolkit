# -*- coding: utf-8 -*-
"""
Schema Validation for Layout Jig state.json
=============================================
Validates required keys, types, enums, and nested structure.

Returns a list of ValidationResult dicts:
  {"level": "error"|"warning", "code": str, "message": str, "path": str}

Python 3 stdlib only.
"""


def _issue(level, code, message, path=""):
    return {"level": level, "code": code, "message": message, "path": path}


# ── Required top-level keys ───────────────────────────

REQUIRED_TOP_KEYS = {
    "schema": str,
    "meta": dict,
    "site": dict,
    "bays": dict,
}

OPTIONAL_TOP_KEYS = {
    "rooms": dict,
    "print_settings": dict,
    "legend": dict,
    "tactile3d": dict,
    "bambu": dict,
    "tts": dict,
    "section": dict,
    "style": dict,
    "capture_jobs": list,
}

REQUIRED_META_KEYS = {
    "last_saved": str,
}

REQUIRED_SITE_KEYS = {
    "width": (int, float),
    "height": (int, float),
}

REQUIRED_BAY_KEYS = {
    "grid_type": str,
    "origin": list,
    "bays": list,
    "spacing": list,
    "corridor": dict,
    "walls": dict,
    "apertures": list,
}

VALID_GRID_TYPES = {"rectangular", "radial"}
VALID_CORRIDOR_AXES = {"x", "y"}
VALID_LOADING_TYPES = {"single", "double", "none"}
VALID_APERTURE_TYPES = {"door", "window", "portal"}
VALID_VOID_SHAPES = {"rectangle", "circle"}


def validate_schema(state):
    """Validate the structural schema of a state dict.

    Returns a list of issues (empty means valid).
    """
    issues = []

    if not isinstance(state, dict):
        return [_issue("error", "not_dict",
                       "State must be a JSON object.", "")]

    # Top-level keys
    for key, expected_type in REQUIRED_TOP_KEYS.items():
        if key not in state:
            issues.append(_issue("error", "missing_key",
                                 "Missing required key '{}'.".format(key),
                                 key))
        elif not isinstance(state[key], expected_type):
            issues.append(_issue("error", "wrong_type",
                                 "Key '{}' should be {} but is {}.".format(
                                     key, expected_type.__name__,
                                     type(state[key]).__name__),
                                 key))

    if issues:
        return issues  # Can't continue without top-level structure

    # Schema version
    schema = state.get("schema", "")
    if not schema.startswith("plan_layout_jig_"):
        issues.append(_issue("warning", "unknown_schema",
                             "Unrecognized schema: '{}'.".format(schema),
                             "schema"))

    # Meta
    meta = state.get("meta", {})
    for key, expected_type in REQUIRED_META_KEYS.items():
        if key not in meta:
            issues.append(_issue("warning", "missing_meta_key",
                                 "Meta missing key '{}'.".format(key),
                                 "meta.{}".format(key)))

    # Site
    site = state.get("site", {})
    for key, expected_type in REQUIRED_SITE_KEYS.items():
        if key not in site:
            issues.append(_issue("error", "missing_site_key",
                                 "Site missing key '{}'.".format(key),
                                 "site.{}".format(key)))
        elif not isinstance(site[key], expected_type):
            issues.append(_issue("error", "wrong_type",
                                 "site.{} should be a number.".format(key),
                                 "site.{}".format(key)))

    # Bays
    bays = state.get("bays", {})
    for bay_name, bay in bays.items():
        prefix = "bays.{}".format(bay_name)
        if not isinstance(bay, dict):
            issues.append(_issue("error", "bay_not_dict",
                                 "Bay {} is not a dict.".format(bay_name),
                                 prefix))
            continue

        for key in REQUIRED_BAY_KEYS:
            if key not in bay:
                issues.append(_issue("error", "missing_bay_key",
                                     "Bay {} missing key '{}'.".format(
                                         bay_name, key),
                                     "{}.{}".format(prefix, key)))

        # Grid type
        gt = bay.get("grid_type", "")
        if gt and gt not in VALID_GRID_TYPES:
            issues.append(_issue("error", "invalid_grid_type",
                                 "Bay {} grid_type '{}' not in {}.".format(
                                     bay_name, gt, VALID_GRID_TYPES),
                                 "{}.grid_type".format(prefix)))

        # Origin must be 2 numbers
        origin = bay.get("origin", [])
        if isinstance(origin, list) and len(origin) != 2:
            issues.append(_issue("error", "bad_origin",
                                 "Bay {} origin must have 2 elements.".format(
                                     bay_name),
                                 "{}.origin".format(prefix)))

        # Corridor
        corridor = bay.get("corridor", {})
        if isinstance(corridor, dict):
            axis = corridor.get("axis", "")
            if axis and axis not in VALID_CORRIDOR_AXES:
                issues.append(_issue("error", "invalid_corridor_axis",
                                     "Bay {} corridor axis '{}' not valid.".format(
                                         bay_name, axis),
                                     "{}.corridor.axis".format(prefix)))
            loading = corridor.get("loading", "")
            if loading and loading not in VALID_LOADING_TYPES:
                issues.append(_issue("warning", "invalid_loading",
                                     "Bay {} corridor loading '{}' not valid.".format(
                                         bay_name, loading),
                                     "{}.corridor.loading".format(prefix)))

        # Apertures
        apertures = bay.get("apertures", [])
        if isinstance(apertures, list):
            seen_ids = set()
            for i, ap in enumerate(apertures):
                ap_path = "{}.apertures[{}]".format(prefix, i)
                if not isinstance(ap, dict):
                    issues.append(_issue("error", "aperture_not_dict",
                                         "Bay {} aperture {} is not a dict.".format(
                                             bay_name, i), ap_path))
                    continue
                ap_id = ap.get("id", "")
                if ap_id in seen_ids:
                    issues.append(_issue("error", "duplicate_aperture_id",
                                         "Bay {} has duplicate aperture id '{}'.".format(
                                             bay_name, ap_id), ap_path))
                seen_ids.add(ap_id)
                ap_type = ap.get("type", "")
                if ap_type and ap_type not in VALID_APERTURE_TYPES:
                    issues.append(_issue("error", "invalid_aperture_type",
                                         "Bay {} aperture {} type '{}' not valid.".format(
                                             bay_name, ap_id, ap_type), ap_path))

    return issues


def format_results(issues):
    """Format validation issues as screen-reader-friendly text."""
    if not issues:
        return "OK: Schema validation passed. No issues."
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
