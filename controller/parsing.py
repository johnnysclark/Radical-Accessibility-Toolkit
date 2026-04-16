# -*- coding: utf-8 -*-
"""
Shared parsing and validation helpers for the Layout Jig controller.

Every command in controller_cli.py tokenizes the same kinds of input:
numbers, "X,Y" coordinate pairs, quoted labels, bay names. Before this
module existed, those coercions were re-implemented per handler with
slightly different error phrasing. The screen-reader contract requires
that "set X <bad-number>" always produces the same kind of ERROR line,
so the phrasing needs to live in one place.

All helpers raise ValueError on bad input with a message that names
the field and echoes the offending token. No prints, no logging --
the REPL owns presentation.

stdlib only. controller_cli.py forbids pip dependencies.
"""

__all__ = [
    "unquote",
    "parse_float",
    "parse_int_pos",
    "parse_int_nn",
    "parse_bay_name",
    "parse_corner",
    "parse_corners",
]


def unquote(s):
    """Strip a single surrounding pair of double quotes, if present.

    The tokenizer preserves quotes on multi-word arguments so that
    `set bay A label "Library Wing"` keeps the label as one token.
    Handlers that consume a user-provided string (label, braille,
    path) call this to recover the raw text.
    """
    if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s


def parse_float(x, name):
    """Coerce to float, or raise ValueError naming the field."""
    try:
        return float(x)
    except (TypeError, ValueError):
        raise ValueError("{} must be a number. Got: {}".format(name, x))


def parse_int_pos(x, name):
    """Coerce to an int >= 1, or raise ValueError naming the field."""
    try:
        v = int(x)
    except (TypeError, ValueError):
        raise ValueError("{} must be a whole number. Got: {}".format(name, x))
    if v < 1:
        raise ValueError("{} must be >= 1. Got: {}".format(name, v))
    return v


def parse_int_nn(x, name):
    """Coerce to an int >= 0, or raise ValueError naming the field."""
    try:
        v = int(x)
    except (TypeError, ValueError):
        raise ValueError("{} must be a whole number. Got: {}".format(name, x))
    if v < 0:
        raise ValueError("{} must be >= 0. Got: {}".format(name, v))
    return v


def parse_bay_name(state, name):
    """Return `name` if it refers to an existing bay, else raise ValueError.

    The error message lists the available bay names so screen-reader
    users hear valid choices after a typo.
    """
    bays = state.get("bays", {})
    if name in bays:
        return name
    avail = ", ".join(sorted(bays)) or "(none)"
    raise ValueError("No bay '{}'. Have: {}".format(name, avail))


def parse_corner(token, name="corner"):
    """Parse a single 'X,Y' token into [x, y] floats."""
    parts = token.split(",")
    if len(parts) != 2:
        raise ValueError("Invalid {} '{}'. Use X,Y format.".format(name, token))
    return [parse_float(parts[0], "{} X".format(name)),
            parse_float(parts[1], "{} Y".format(name))]


def parse_corners(tokens, minimum=3, name="corner"):
    """Parse a list of 'X,Y' tokens into [[x, y], ...].

    Enforces `minimum` pairs so polygon handlers can demand at least
    three points without repeating the length check.
    """
    if len(tokens) < minimum:
        raise ValueError(
            "Need at least {} {} pairs (X,Y). Got {}.".format(
                minimum, name, len(tokens)))
    return [parse_corner(t, name) for t in tokens]
