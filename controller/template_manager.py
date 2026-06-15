# -*- coding: utf-8 -*-
"""
TEMPLATE MANAGER — startup state generators
===========================================
A *template* produces a complete state.json from a small set of named
parameters. Different from a macro: a template replaces the whole state,
a macro replays commands on the existing state.

Templates live as Python modules in ``controller/templates/``. Each module
exposes:

  NAME         str   — the name used on the command line.
  DESCRIPTION  str   — one-line summary.
  PARAMS       list  — parameters, each a ``(key, default, help)`` tuple
                       (or a dict with those keys).
  build(params) -> dict
                     — returns a full state dict from the merged params.

This module is stdlib-only (controller rule) and screen-reader friendly:
every public function returns short, labeled, single-line output.
"""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(_HERE, "templates")


# ── discovery ─────────────────────────────────────────────

def _iter_template_files():
    if not os.path.isdir(TEMPLATES_DIR):
        return
    for fn in sorted(os.listdir(TEMPLATES_DIR)):
        if fn.endswith(".py") and not fn.startswith("_"):
            yield os.path.join(TEMPLATES_DIR, fn)


def _load_module(path):
    mod_name = "jig_template_" + os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _normalize_params(mod):
    """Return params as a list of {key, default, help} dicts."""
    out = []
    for p in getattr(mod, "PARAMS", []):
        if isinstance(p, dict):
            out.append({"key": p["key"],
                        "default": p.get("default"),
                        "help": p.get("help", "")})
        else:
            seq = list(p) + ["", ""]
            out.append({"key": seq[0], "default": seq[1], "help": seq[2]})
    return out


def _all_templates():
    """Map template name -> loaded module. Skips modules that fail to import."""
    res = {}
    for path in _iter_template_files():
        try:
            mod = _load_module(path)
        except Exception:
            continue
        name = getattr(mod, "NAME", None) or \
            os.path.splitext(os.path.basename(path))[0]
        if hasattr(mod, "build"):
            res[name] = mod
    return res


# ── public API (used by controller_cli and the MCP server) ──

def list_templates():
    out = []
    for name, mod in sorted(_all_templates().items()):
        out.append({"name": name,
                    "description": getattr(mod, "DESCRIPTION", ""),
                    "params": _normalize_params(mod)})
    return out


def format_template_list(templates):
    if not templates:
        return "OK: No templates found.\nREADY:"
    lines = ["OK: {0} template(s) available:".format(len(templates))]
    for t in templates:
        lines.append("  {0}  ({1} param(s))".format(
            t["name"], len(t["params"])))
        if t["description"]:
            lines.append("    {0}".format(t["description"]))
    lines.append("READY:")
    return "\n".join(lines)


def _get(name):
    mods = _all_templates()
    if name not in mods:
        avail = ", ".join(sorted(mods)) or "(none)"
        raise ValueError("No template '{0}'. Available: {1}".format(name, avail))
    return mods[name]


def show_template(name):
    mod = _get(name)
    params = _normalize_params(mod)
    lines = ["OK: Template '{0}'".format(name)]
    desc = getattr(mod, "DESCRIPTION", "")
    if desc:
        lines.append("  {0}".format(desc))
    lines.append("  Parameters: {0}".format(len(params)))
    for p in params:
        lines.append("    {0} = {1}".format(p["key"], p["default"]))
        if p["help"]:
            lines.append("      {0}".format(p["help"]))
    lines.append("  Usage: template load {0} key=value ...".format(name))
    lines.append("READY:")
    return "\n".join(lines)


def generate(name, overrides=None):
    """Build a fresh state dict from a template plus optional overrides.

    ``overrides`` is a dict (already parsed by the caller). Unknown keys
    raise ValueError so a typo never silently does nothing.
    """
    mod = _get(name)
    overrides = overrides or {}
    params = {p["key"]: p["default"] for p in _normalize_params(mod)}
    unknown = [k for k in overrides if k not in params]
    if unknown:
        raise ValueError(
            "Unknown parameter(s) for '{0}': {1}. Valid: {2}".format(
                name, ", ".join(sorted(unknown)), ", ".join(sorted(params))))
    params.update(overrides)
    state = mod.build(params)
    if not isinstance(state, dict) or "bays" not in state:
        raise ValueError(
            "Template '{0}' build() did not return a valid state.".format(name))
    return state
