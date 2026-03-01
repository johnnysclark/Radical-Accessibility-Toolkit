# -*- coding: utf-8 -*-
"""
PLAN LAYOUT JIG — Skill Engine  v1.0
======================================
Stores, lists, and replays reusable command sequences ("skills").

A skill is a JSON file in the skills/ folder containing:
  - name: kebab-case identifier
  - description: what the skill does
  - version: integer
  - commands: list of CLI command strings with {param} placeholders
  - params: dict of param_name -> {description, default}

Skills are the Layout Jig equivalent of macros — named sequences of
controller commands that can be saved once and replayed with different
parameters.

Requires: Python 3 stdlib only.
"""

import json
import os
import re

# ── Paths ──────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(_here, "skills")


# ══════════════════════════════════════════════════════════
# SKILL FILE FORMAT
# ══════════════════════════════════════════════════════════

_SKILL_SCHEMA = {
    "name": str,
    "description": str,
    "version": int,
    "commands": list,
    "params": dict,
}

_EXAMPLE_SKILL = {
    "name": "add-double-loaded-corridor",
    "description": "Enable a double-loaded corridor on a bay with doors on both ends.",
    "version": 1,
    "commands": [
        "corridor {bay} on",
        "corridor {bay} axis {axis}",
        "corridor {bay} width {width}",
        "corridor {bay} loading double",
    ],
    "params": {
        "bay": {"description": "Target bay name", "default": "A"},
        "axis": {"description": "Corridor axis (x or y)", "default": "x"},
        "width": {"description": "Corridor width in feet", "default": "8"},
    }
}


def _ensure_skills_dir():
    """Create the skills/ folder if it does not exist."""
    os.makedirs(SKILLS_DIR, exist_ok=True)


def _skill_path(name):
    """Return the file path for a skill by name."""
    safe = re.sub(r'[^a-z0-9_-]', '-', name.lower().strip())
    return os.path.join(SKILLS_DIR, f"{safe}.json")


def _validate_skill(data):
    """Validate a skill dict. Returns list of error strings (empty = valid)."""
    errors = []
    for key, expected_type in _SKILL_SCHEMA.items():
        if key not in data:
            errors.append(f"Missing required field: '{key}'")
        elif not isinstance(data[key], expected_type):
            errors.append(f"Field '{key}' must be {expected_type.__name__}, "
                          f"got {type(data[key]).__name__}")

    if "commands" in data and isinstance(data["commands"], list):
        if len(data["commands"]) == 0:
            errors.append("Commands list must not be empty.")
        for i, cmd in enumerate(data["commands"]):
            if not isinstance(cmd, str):
                errors.append(f"Command {i} must be a string.")

    if "params" in data and isinstance(data["params"], dict):
        for pname, pval in data["params"].items():
            if not isinstance(pval, dict):
                errors.append(f"Param '{pname}' must be a dict with "
                              f"'description' and 'default'.")
            elif "default" not in pval:
                errors.append(f"Param '{pname}' missing 'default' field.")

    return errors


# ══════════════════════════════════════════════════════════
# PUBLIC API
# ══════════════════════════════════════════════════════════

def list_skills():
    """List all saved skills.

    Returns a list of dicts: [{name, description, command_count, path}, ...]
    """
    _ensure_skills_dir()
    result = []
    for fname in sorted(os.listdir(SKILLS_DIR)):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(SKILLS_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            result.append({
                "name": data.get("name", fname[:-5]),
                "description": data.get("description", "(no description)"),
                "command_count": len(data.get("commands", [])),
                "param_count": len(data.get("params", {})),
                "path": fpath,
            })
        except (json.JSONDecodeError, OSError):
            result.append({
                "name": fname[:-5],
                "description": "(error reading file)",
                "command_count": 0,
                "param_count": 0,
                "path": fpath,
            })
    return result


def format_skill_list(skills):
    """Format skill list for screen reader output."""
    if not skills:
        return "OK: No skills saved yet. Use skill_save to create one.\nREADY:"

    lines = [f"OK: {len(skills)} skill(s) available.", ""]
    for i, sk in enumerate(skills, 1):
        lines.append(f"  {i}. {sk['name']}")
        lines.append(f"     {sk['description']}")
        lines.append(f"     {sk['command_count']} command(s), {sk['param_count']} param(s)")
    lines.append("READY:")
    return "\n".join(lines)


def load_skill(name):
    """Load a skill by name. Returns the skill dict or raises ValueError."""
    path = _skill_path(name)
    if not os.path.isfile(path):
        # Try finding by partial match
        _ensure_skills_dir()
        available = [f[:-5] for f in os.listdir(SKILLS_DIR)
                     if f.endswith(".json")]
        matches = [a for a in available if name.lower() in a.lower()]
        if len(matches) == 1:
            path = os.path.join(SKILLS_DIR, f"{matches[0]}.json")
        elif matches:
            raise ValueError(
                f"Skill '{name}' not found. Did you mean: {', '.join(matches)}?")
        else:
            avail_str = ', '.join(available) if available else '(none)'
            raise ValueError(
                f"Skill '{name}' not found. Available: {avail_str}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    errors = _validate_skill(data)
    if errors:
        raise ValueError(f"Skill '{name}' has validation errors: {'; '.join(errors)}")

    return data


def format_skill_detail(skill):
    """Format a single skill for detailed screen reader output."""
    lines = [f"OK: Skill '{skill['name']}' (v{skill.get('version', 1)})", ""]
    lines.append(f"  Description: {skill['description']}")
    lines.append("")

    # Parameters
    params = skill.get("params", {})
    if params:
        lines.append(f"  Parameters ({len(params)}):")
        for pname, pval in sorted(params.items()):
            lines.append(f"    {{{pname}}}: {pval.get('description', '?')}  "
                         f"(default: {pval.get('default', '?')})")
        lines.append("")

    # Commands
    commands = skill.get("commands", [])
    lines.append(f"  Commands ({len(commands)}):")
    for i, cmd in enumerate(commands, 1):
        lines.append(f"    {i}. {cmd}")

    lines.append("READY:")
    return "\n".join(lines)


def save_skill(name, description, commands, params=None):
    """Save a new skill to the skills/ folder.

    Args:
        name: kebab-case skill name (e.g. "add-double-loaded-corridor")
        description: what the skill does
        commands: list of CLI command strings with {param} placeholders
        params: dict of param_name -> {description, default}

    Returns: confirmation message string.
    """
    if params is None:
        # Auto-detect params from {placeholders} in commands
        params = {}
        for cmd in commands:
            for match in re.finditer(r'\{(\w+)\}', cmd):
                pname = match.group(1)
                if pname not in params:
                    params[pname] = {"description": f"Value for {pname}", "default": ""}

    skill = {
        "name": name,
        "description": description,
        "version": 1,
        "commands": commands,
        "params": params,
    }

    errors = _validate_skill(skill)
    if errors:
        return f"ERROR: Skill validation failed: {'; '.join(errors)}"

    _ensure_skills_dir()
    path = _skill_path(name)

    # Check for overwrite
    existed = os.path.isfile(path)

    # Atomic write
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(skill, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)

    action = "Updated" if existed else "Saved"
    return (f"OK: {action} skill '{name}' with {len(commands)} command(s) "
            f"and {len(params)} param(s) to {path}")


def run_skill(name, overrides, run_fn):
    """Execute a saved skill, substituting parameters.

    Args:
        name: skill name to load
        overrides: dict of param_name -> value (overrides defaults)
        run_fn: callable that takes a command string and returns a message
                (this is mcp_server._run)

    Returns: combined output from all commands.
    """
    try:
        skill = load_skill(name)
    except ValueError as e:
        return f"ERROR: {e}"

    # Build final param values: defaults + overrides
    params = {}
    for pname, pval in skill.get("params", {}).items():
        params[pname] = pval.get("default", "")
    if overrides:
        for k, v in overrides.items():
            params[k] = v

    # Check for unresolved params
    commands = skill["commands"]
    resolved = []
    for cmd in commands:
        result = cmd
        for pname, pval in params.items():
            result = result.replace(f"{{{pname}}}", str(pval))
        # Check for remaining {placeholders}
        remaining = re.findall(r'\{(\w+)\}', result)
        if remaining:
            return (f"ERROR: Unresolved parameter(s) in command '{cmd}': "
                    f"{', '.join(remaining)}. Provide values for these.")
        resolved.append(result)

    # Execute each command
    lines = [f"OK: Running skill '{skill['name']}' ({len(resolved)} commands)", ""]
    all_ok = True
    for i, cmd in enumerate(resolved, 1):
        msg = run_fn(cmd)
        prefix = "OK" if not msg.startswith("ERROR") else "FAIL"
        lines.append(f"  {i}. [{prefix}] {cmd}")
        if msg:
            # Indent the output
            for mline in msg.split("\n"):
                lines.append(f"       {mline}")
        if msg.startswith("ERROR"):
            all_ok = False
            lines.append(f"  Stopped at command {i} due to error.")
            break

    lines.append("")
    if all_ok:
        lines.append(f"Skill '{skill['name']}' completed: {len(resolved)} command(s) executed.")
    else:
        lines.append(f"Skill '{skill['name']}' failed.")
    lines.append("READY:")
    return "\n".join(lines)


def create_example_skill():
    """Write the example skill to skills/ for documentation purposes."""
    return save_skill(
        _EXAMPLE_SKILL["name"],
        _EXAMPLE_SKILL["description"],
        _EXAMPLE_SKILL["commands"],
        _EXAMPLE_SKILL["params"],
    )
