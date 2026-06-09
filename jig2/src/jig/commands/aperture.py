"""Aperture commands: doors, windows, portals on bay walls."""

from jig.commands.registry import CommandError, command
from jig.commands.util import (fmt, need_args, need_bay, need_choice,
                               to_float, to_int)
from jig.model.io import mint_id
from jig.model.schema import APERTURE_KINDS, AXES, HINGES, SWINGS, Aperture


@command("aperture add",
         "aperture add BAY door|window|portal --axis x|y --line N --offset F "
         "--width W [--hinge start|end] [--swing in|out]",
         "Add a door, window, or portal to a bay wall.")
def aperture_add(session, args, flags):
    need_args(args, 2, "aperture add BAY KIND --axis x --line 0 --offset 10 --width 3")
    bay = need_bay(session, args[0].lower())
    kind = need_choice(args[1], APERTURE_KINDS, "aperture kind")
    for required in ("axis", "line", "offset", "width"):
        if required not in flags:
            raise CommandError("aperture add needs --{}. Usage: aperture add BAY "
                               "KIND --axis x --line 0 --offset 10 --width 3".format(required))
    axis = need_choice(str(flags["axis"]), AXES, "axis")
    line = to_int(flags["line"], "line")
    max_line = bay.counts[1] if axis == "x" else bay.counts[0]
    if not (0 <= line <= max_line):
        raise CommandError("bay {} has lines 0 to {} on axis {}, got {}".format(
            bay.name, max_line, axis, line))
    offset = to_float(flags["offset"], "offset")
    width = to_float(flags["width"], "width")
    run = bay.width if axis == "x" else bay.depth
    if offset + width > run:
        raise CommandError("that aperture ends at {} but the wall is only {} long".format(
            fmt(offset + width), fmt(run)))
    ap = Aperture(id=mint_id("ap", session.state.all_ids()), kind=kind,
                  axis=axis, line=line, offset=offset, width=width,
                  hinge=need_choice(str(flags.get("hinge", "start")), HINGES, "hinge"),
                  swing=need_choice(str(flags.get("swing", "in")), SWINGS, "swing"))
    bay.apertures.append(ap)
    return "{} {} added to bay {}, axis {} line {}, offset {}, width {}".format(
        kind, ap.id, bay.name, axis, line, fmt(offset), fmt(width))


@command("aperture remove", "aperture remove BAY ID", "Remove an aperture by id.")
def aperture_remove(session, args, flags):
    need_args(args, 2, "aperture remove BAY ID")
    bay = need_bay(session, args[0].lower())
    ap = bay.find_aperture(args[1])
    if ap is None:
        ids = ", ".join(a.id for a in bay.apertures) or "none"
        raise CommandError("no aperture {} in bay {}. Apertures: {}".format(
            args[1], bay.name, ids))
    bay.apertures.remove(ap)
    return "{} {} removed from bay {}".format(ap.kind, ap.id, bay.name)


@command("aperture list", "aperture list BAY", "List a bay's apertures.", mutating=False)
def aperture_list(session, args, flags):
    need_args(args, 1, "aperture list BAY")
    bay = need_bay(session, args[0].lower())
    if not bay.apertures:
        return "bay {} has no apertures".format(bay.name)
    lines = ["bay {} has {} apertures".format(bay.name, len(bay.apertures))]
    for ap in bay.apertures:
        detail = ""
        if ap.kind == "door":
            detail = ", hinge {}, swings {}".format(ap.hinge, ap.swing)
        lines.append("{} {}: axis {} line {}, offset {}, width {}{}".format(
            ap.kind, ap.id, ap.axis, ap.line, fmt(ap.offset), fmt(ap.width), detail))
    return "\n".join(lines)
