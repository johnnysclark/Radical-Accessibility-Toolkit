"""Zone commands."""

from jig.commands.registry import CommandError, command
from jig.commands.util import (fmt, need_args, need_choice, parse_point,
                               parse_polygon, to_float)
from jig.model.io import mint_id
from jig.model.schema import ZONE_KINDS, Zone


@command("zone add", "zone add NAME WIDTH DEPTH --at X,Y [--kind KIND] [--label TEXT]",
         "Add a rectangular program zone.")
def zone_add(session, args, flags):
    need_args(args, 3, "zone add NAME WIDTH DEPTH --at X,Y")
    name = args[0]
    if session.state.find_zone(name):
        raise CommandError("a zone named {} already exists".format(name))
    w = to_float(args[1], "width")
    d = to_float(args[2], "depth")
    ox, oy = parse_point(flags.get("at", "0,0"), "at")
    kind = need_choice(flags.get("kind", "program"), ZONE_KINDS, "kind")
    zone = Zone(id=mint_id("z", session.state.all_ids()), name=name,
                boundary=[[ox, oy], [ox + w, oy], [ox + w, oy + d], [ox, oy + d]],
                label=str(flags.get("label", "")), kind=kind)
    session.state.zones.append(zone)
    return "zone {} added, {} by {} at {},{}".format(name, fmt(w), fmt(d), fmt(ox), fmt(oy))


@command("zone polygon", "zone polygon NAME X,Y X,Y X,Y ... [--kind KIND] [--label TEXT]",
         "Add a polygonal program zone.")
def zone_polygon(session, args, flags):
    need_args(args, 4, "zone polygon NAME X,Y X,Y X,Y")
    name = args[0]
    if session.state.find_zone(name):
        raise CommandError("a zone named {} already exists".format(name))
    boundary = parse_polygon(args[1:])
    kind = need_choice(flags.get("kind", "program"), ZONE_KINDS, "kind")
    zone = Zone(id=mint_id("z", session.state.all_ids()), name=name,
                boundary=boundary, label=str(flags.get("label", "")), kind=kind)
    session.state.zones.append(zone)
    return "zone {} added with {} corners".format(name, len(boundary))


@command("zone remove", "zone remove NAME", "Remove a zone.")
def zone_remove(session, args, flags):
    need_args(args, 1, "zone remove NAME")
    zone = session.state.find_zone(args[0])
    if zone is None:
        raise CommandError("no zone named {}".format(args[0]))
    session.state.zones.remove(zone)
    return "zone {} removed".format(zone.name)


@command("zone list", "zone list", "List all zones.", mutating=False)
def zone_list(session, args, flags):
    if not session.state.zones:
        return "no zones"
    lines = ["{} zones".format(len(session.state.zones))]
    for z in session.state.zones:
        lines.append("zone {}: {} kind, {} corners, label {}".format(
            z.name, z.kind, len(z.boundary), z.label))
    return "\n".join(lines)
