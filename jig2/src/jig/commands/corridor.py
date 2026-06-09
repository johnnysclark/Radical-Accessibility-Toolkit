"""Corridor commands."""

from jig.commands.registry import CommandError, command
from jig.commands.util import (fmt, need_args, need_bay, need_choice,
                               to_float, to_int)
from jig.model.schema import AXES, Corridor


@command("corridor", "corridor BAY on|off [--axis x|y] [--line N] [--width W]",
         "Carve a corridor through a bay along an interior gridline.")
def corridor(session, args, flags):
    need_args(args, 2, "corridor BAY on|off --axis x --line 1 --width 8")
    bay = need_bay(session, args[0].lower())
    setting = need_choice(args[1], ("on", "off"), "corridor setting")
    if setting == "off":
        bay.corridor = None
        return "bay {} corridor off".format(bay.name)
    axis = need_choice(str(flags.get("axis", "x")), AXES, "axis")
    line = to_int(flags.get("line", 1), "line")
    width = to_float(flags.get("width", 8.0), "width")
    max_line = bay.counts[1] if axis == "x" else bay.counts[0]
    if not (1 <= line <= max_line - 1):
        raise CommandError("corridor line must be an interior line, 1 to {}, got {}".format(
            max_line - 1, line))
    bay.corridor = Corridor(axis=axis, line=line, width=width)
    return "bay {} corridor on, axis {} line {}, width {}".format(
        bay.name, axis, line, fmt(width))
