"""Global structural grid commands."""

from jig.commands.registry import command
from jig.commands.util import fmt, need_args, parse_point, to_float
from jig.model.schema import Grid


@command("grid set", "grid set SPACING_X [SPACING_Y] [--rotation DEG] [--origin X,Y]",
         "Turn on the site-wide structural grid.")
def grid_set(session, args, flags):
    need_args(args, 1, "grid set SPACING_X [SPACING_Y]")
    sx = to_float(args[0], "spacing")
    sy = to_float(args[1], "spacing") if len(args) > 1 else sx
    rotation = to_float(flags.get("rotation", 0), "rotation")
    origin = parse_point(flags.get("origin", "0,0"), "origin")
    session.state.grid = Grid(enabled=True, spacing=[sx, sy],
                              rotation_deg=rotation, origin=origin)
    return "grid on, spacing {} by {}, rotation {} degrees".format(
        fmt(sx), fmt(sy), fmt(rotation))


@command("grid off", "grid off", "Turn off the site-wide structural grid.")
def grid_off(session, args, flags):
    session.state.grid.enabled = False
    return "grid off"
