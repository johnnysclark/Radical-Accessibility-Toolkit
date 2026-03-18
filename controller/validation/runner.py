# -*- coding: utf-8 -*-
"""
Validation Runner — Runs all validation layers on a state dict.
================================================================
Provides unified entry points for CLI and MCP:
  validate_state(state)    — schema + semantic
  validate_model(state)    — schema + semantic + spatial
  validate_tactile_output(state) — all above + tactile
  validate_fabrication_output(state) — all above + fabrication
  validate_all(state)      — every layer

Python 3 stdlib only.
"""
from controller.validation import schema as schema_mod
from controller.validation import semantic as semantic_mod
from controller.validation import spatial as spatial_mod
from controller.validation import tactile as tactile_mod
from controller.validation import fabrication as fab_mod


def validate_state(state):
    """Schema + semantic validation. Returns dict with results."""
    results = {
        "schema": schema_mod.validate_schema(state),
        "semantic": semantic_mod.validate_semantic(state),
    }
    results["all_issues"] = results["schema"] + results["semantic"]
    results["error_count"] = sum(1 for i in results["all_issues"] if i["level"] == "error")
    results["warning_count"] = sum(1 for i in results["all_issues"] if i["level"] == "warning")
    results["valid"] = results["error_count"] == 0
    return results


def validate_model(state):
    """Schema + semantic + spatial validation."""
    results = validate_state(state)
    spatial_issues = spatial_mod.validate_spatial(state)
    results["spatial"] = spatial_issues
    results["all_issues"] = results["all_issues"] + spatial_issues
    results["error_count"] = sum(1 for i in results["all_issues"] if i["level"] == "error")
    results["warning_count"] = sum(1 for i in results["all_issues"] if i["level"] == "warning")
    results["valid"] = results["error_count"] == 0
    return results


def validate_tactile_output(state):
    """All model validation + tactile checks."""
    results = validate_model(state)
    tactile_issues = tactile_mod.validate_tactile(state)
    results["tactile"] = tactile_issues
    results["all_issues"] = results["all_issues"] + tactile_issues
    results["error_count"] = sum(1 for i in results["all_issues"] if i["level"] == "error")
    results["warning_count"] = sum(1 for i in results["all_issues"] if i["level"] == "warning")
    results["valid"] = results["error_count"] == 0
    return results


def validate_fabrication_output(state):
    """All model validation + fabrication checks."""
    results = validate_model(state)
    fab_issues = fab_mod.validate_fabrication(state)
    results["fabrication"] = fab_issues
    results["all_issues"] = results["all_issues"] + fab_issues
    results["error_count"] = sum(1 for i in results["all_issues"] if i["level"] == "error")
    results["warning_count"] = sum(1 for i in results["all_issues"] if i["level"] == "warning")
    results["valid"] = results["error_count"] == 0
    return results


def validate_all(state):
    """Run every validation layer."""
    results = {
        "schema": schema_mod.validate_schema(state),
        "semantic": semantic_mod.validate_semantic(state),
        "spatial": spatial_mod.validate_spatial(state),
        "tactile": tactile_mod.validate_tactile(state),
        "fabrication": fab_mod.validate_fabrication(state),
    }
    all_issues = []
    for layer in ("schema", "semantic", "spatial", "tactile", "fabrication"):
        all_issues.extend(results[layer])
    results["all_issues"] = all_issues
    results["error_count"] = sum(1 for i in all_issues if i["level"] == "error")
    results["warning_count"] = sum(1 for i in all_issues if i["level"] == "warning")
    results["valid"] = results["error_count"] == 0
    return results


def format_results(results):
    """Format combined validation results for screen readers."""
    issues = results.get("all_issues", [])
    if not issues:
        return "OK: All validation passed. No issues."

    lines = []
    errors = results.get("error_count", 0)
    warnings = results.get("warning_count", 0)
    lines.append("{} issues ({} errors, {} warnings):".format(
        len(issues), errors, warnings))
    for idx, issue in enumerate(issues, 1):
        level = issue["level"].upper()
        lines.append("  {}. {}: {} [{}]".format(
            idx, level, issue["message"], issue["path"]))
    return "\n".join(lines)
