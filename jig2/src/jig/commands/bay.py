"""Bay commands: rectangular structural grids of columns."""

from jig.commands.registry import CommandError, command
from jig.commands.util import (fmt, need_args, need_bay, parse_counts,
                               parse_number_list, parse_point, to_float)
from jig.model.io import mint_id
from jig.model.schema import Bay


def _spacings(flags, nx, ny):
    if "spacing-x" in flags or "spacing-y" in flags:
        sx = parse_number_list(flags.get("spacing-x", "24"), "spacing-x")
        sy = parse_number_list(flags.get("spacing-y", "24"), "spacing-y")
        if len(sx) == 1:
            sx = sx * nx
        if len(sy) == 1:
            sy = sy * ny
        return sx, sy
    spacing = parse_number_list(str(flags.get("spacing", "24")), "spacing")
    if len(spacing) == 1:
        return [spacing[0]] * nx, [spacing[0]] * ny
    if len(spacing) == 2:
        return [spacing[0]] * nx, [spacing[1]] * ny
    raise CommandError("spacing takes one number, or two as SX,SY; "
                       "use spacing-x and spacing-y for irregular grids")


@command("bay add", "bay add NAME NxM [--spacing S | SX,SY] [--spacing-x LIST] "
                    "[--spacing-y LIST] [--at X,Y] [--rotation DEG]",
         "Add a rectangular bay grid: N bays across x, M across y.")
def bay_add(session, args, flags):
    need_args(args, 2, "bay add NAME NxM --spacing 24 --at X,Y")
    name = args[0].lower()
    if session.state.find_bay(name):
        raise CommandError("a bay named {} already exists".format(name))
    nx, ny = parse_counts(args[1])
    spacing_x, spacing_y = _spacings(flags, nx, ny)
    bay = Bay(id=mint_id("b", session.state.all_ids()), name=name,
              origin=parse_point(flags.get("at", "0,0"), "at"),
              rotation_deg=to_float(flags.get("rotation", 0), "rotation"),
              counts=[nx, ny], spacing_x=spacing_x, spacing_y=spacing_y)
    session.state.bays.append(bay)
    columns = (nx + 1) * (ny + 1)
    return "bay {} added, {} by {} bays, {} by {} {}, {} columns".format(
        name, nx, ny, fmt(bay.width), fmt(bay.depth), session.state.units, columns)


@command("bay set", "bay set NAME rotation DEG | origin X,Y | counts NxM | spacing S [SY]",
         "Change one property of a bay.")
def bay_set(session, args, flags):
    need_args(args, 3, "bay set NAME PROPERTY VALUE")
    bay = need_bay(session, args[0].lower())
    prop, value = args[1], args[2]
    if prop == "rotation":
        bay.rotation_deg = to_float(value, "rotation")
        return "bay {} rotation set to {} degrees".format(bay.name, fmt(bay.rotation_deg))
    if prop == "origin":
        bay.origin = parse_point(value, "origin")
        return "bay {} moved to {},{}".format(bay.name, fmt(bay.origin[0]), fmt(bay.origin[1]))
    if prop == "counts":
        nx, ny = parse_counts(value)
        sx = bay.spacing_x[0] if bay.spacing_x else 24.0
        sy = bay.spacing_y[0] if bay.spacing_y else 24.0
        bay.counts = [nx, ny]
        bay.spacing_x = [sx] * nx
        bay.spacing_y = [sy] * ny
        return "bay {} resized to {} by {} bays".format(bay.name, nx, ny)
    if prop == "spacing":
        sx = to_float(value, "spacing")
        sy = to_float(args[3], "spacing") if len(args) > 3 else sx
        bay.spacing_x = [sx] * bay.counts[0]
        bay.spacing_y = [sy] * bay.counts[1]
        return "bay {} spacing set to {} by {}".format(bay.name, fmt(sx), fmt(sy))
    raise CommandError("bay set knows rotation, origin, counts, spacing; got {}".format(prop))


@command("bay remove", "bay remove NAME", "Remove a bay and everything in it.")
def bay_remove(session, args, flags):
    need_args(args, 1, "bay remove NAME")
    bay = need_bay(session, args[0].lower())
    session.state.bays.remove(bay)
    return "bay {} removed".format(bay.name)


@command("bay list", "bay list", "List all bays.", mutating=False)
def bay_list(session, args, flags):
    if not session.state.bays:
        return "no bays"
    lines = ["{} bays".format(len(session.state.bays))]
    for b in session.state.bays:
        extras = []
        if b.walls.enabled:
            extras.append("walls on")
        if b.corridor:
            extras.append("corridor on {} axis".format(b.corridor.axis))
        if b.apertures:
            extras.append("{} apertures".format(len(b.apertures)))
        suffix = ", " + ", ".join(extras) if extras else ""
        lines.append("bay {}: {} by {} bays at {},{}{}".format(
            b.name, b.counts[0], b.counts[1],
            fmt(b.origin[0]), fmt(b.origin[1]), suffix))
    return "\n".join(lines)
