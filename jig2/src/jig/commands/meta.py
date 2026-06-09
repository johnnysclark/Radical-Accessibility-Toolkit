"""Read-only commands: describe, status, help, validate, measure. Plus void."""

import math

from jig import describe as describe_mod
from jig.commands.registry import CommandError, all_commands, command
from jig.commands.util import (fmt, need_args, need_bay, need_choice,
                               parse_point, to_float)
from jig.geometry.bays import bay_center, cell_center
from jig.model.io import mint_id
from jig.model.schema import Void
from jig.model.validate import validate as validate_state


@command("describe", "describe [meta|site|zones|grid|bays]",
         "Describe the whole model, or one section, in prose.", mutating=False)
def describe(session, args, flags):
    section = args[0] if args else "all"
    return describe_mod.describe(session.state, section)


@command("status", "status", "One-line model summary.", mutating=False)
def status(session, args, flags):
    return describe_mod.status(session.state)


@command("help", "help [COMMAND]", "List commands, or show one command's usage.",
         mutating=False)
def help_cmd(session, args, flags):
    if args:
        prefix = tuple(a.lower() for a in args)
        matches = [s for s in all_commands() if s.words[:len(prefix)] == prefix]
        if not matches:
            raise CommandError("no command starts with {}".format(" ".join(args)))
        return "\n".join("{}\n  {}".format(s.usage, s.summary) for s in matches)
    lines = ["{} commands. Say help COMMAND for usage.".format(len(all_commands()))]
    for s in all_commands():
        lines.append("{}: {}".format(" ".join(s.words), s.summary))
    return "\n".join(lines)


@command("validate", "validate", "Check the model for semantic problems.",
         mutating=False)
def validate(session, args, flags):
    findings = validate_state(session.state)
    if not findings:
        return "model is clean, no findings"
    lines = ["{} findings".format(len(findings))]
    lines += findings
    return "\n".join(lines)


@command("measure", "measure NAME NAME", "Distance between two named things "
         "(bays, zones, or cells as BAY/I,J).", mutating=False)
def measure(session, args, flags):
    need_args(args, 2, "measure NAME NAME")
    a = _locate(session.state, args[0])
    b = _locate(session.state, args[1])
    distance = math.hypot(b[0] - a[0], b[1] - a[1])
    return "distance from {} to {} is {} {}, center to center".format(
        args[0], args[1], fmt(round(distance, 2)), session.state.units)


def _locate(state, name):
    """Resolve a name to a world point: bay, zone, or cell as BAY/I,J."""
    if "/" in name:
        bay_name, _, cell_part = name.partition("/")
        bay = state.find_bay(bay_name.lower())
        if bay:
            try:
                i, j = (int(v) for v in cell_part.split(","))
            except ValueError:
                raise CommandError("cell address must look like BAY/I,J, got {}".format(name))
            return cell_center(bay, i, j)
    bay = state.find_bay(name.lower())
    if bay:
        return bay_center(bay)
    zone = state.find_zone(name)
    if zone:
        n = float(len(zone.boundary))
        return (sum(p[0] for p in zone.boundary) / n,
                sum(p[1] for p in zone.boundary) / n)
    raise CommandError("nothing named {}. Try a bay name, zone name, or BAY/I,J".format(name))


@command("void add", "void add BAY rect|circle --at X,Y --size W[,D]",
         "Cut a void in a bay, centered at bay-local X,Y.")
def void_add(session, args, flags):
    need_args(args, 2, "void add BAY rect --at 30,20 --size 20,12")
    bay = need_bay(session, args[0].lower())
    shape = need_choice(args[1], ("rect", "circle"), "void shape")
    if "at" not in flags or "size" not in flags:
        raise CommandError("void add needs --at X,Y and --size W or W,D")
    center = parse_point(flags["at"], "at")
    size_parts = str(flags["size"]).split(",")
    w = to_float(size_parts[0], "size")
    d = to_float(size_parts[1], "size") if len(size_parts) > 1 else w
    void = Void(id=mint_id("v", session.state.all_ids()), shape=shape,
                center=center, size=[w, d])
    bay.voids.append(void)
    return "void {} added to bay {}, {} {} by {}".format(
        void.id, bay.name, shape, fmt(w), fmt(d))


@command("void remove", "void remove BAY ID", "Remove a void.")
def void_remove(session, args, flags):
    need_args(args, 2, "void remove BAY ID")
    bay = need_bay(session, args[0].lower())
    for void in bay.voids:
        if void.id == args[1]:
            bay.voids.remove(void)
            return "void {} removed from bay {}".format(void.id, bay.name)
    ids = ", ".join(v.id for v in bay.voids) or "none"
    raise CommandError("no void {} in bay {}. Voids: {}".format(args[1], bay.name, ids))
