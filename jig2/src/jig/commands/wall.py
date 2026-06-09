"""Wall commands."""

from jig.commands.registry import command
from jig.commands.util import fmt, need_args, need_bay, need_choice, to_float


@command("wall", "wall BAY on|off [--thickness T]",
         "Turn a bay's gridline walls on or off.")
def wall(session, args, flags):
    need_args(args, 2, "wall BAY on|off")
    bay = need_bay(session, args[0].lower())
    setting = need_choice(args[1], ("on", "off"), "wall setting")
    bay.walls.enabled = setting == "on"
    if "thickness" in flags:
        bay.walls.thickness = to_float(flags["thickness"], "thickness")
    if bay.walls.enabled:
        return "bay {} walls on, thickness {}".format(bay.name, fmt(bay.walls.thickness))
    return "bay {} walls off".format(bay.name)
