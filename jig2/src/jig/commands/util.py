"""Shared argument parsing for command handlers. All errors are speakable."""

from jig.commands.registry import CommandError


def to_float(value, what):
    try:
        return float(value)
    except (TypeError, ValueError):
        raise CommandError("{} must be a number, got {!r}".format(what, value))


def to_int(value, what):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise CommandError("{} must be a whole number, got {!r}".format(what, value))


def parse_point(value, what="point"):
    """Parse 'X,Y' into [x, y]."""
    parts = str(value).split(",")
    if len(parts) != 2:
        raise CommandError("{} must look like X,Y — for example 18,8".format(what))
    return [to_float(parts[0], what + " x"), to_float(parts[1], what + " y")]


def parse_counts(value):
    """Parse 'NxM' into (n, m)."""
    parts = str(value).lower().split("x")
    if len(parts) != 2:
        raise CommandError("counts must look like NxM — for example 6x4")
    return to_int(parts[0], "count n"), to_int(parts[1], "count m")


def parse_number_list(value, what):
    """Parse '24,30,24' into floats."""
    values = [to_float(v, what) for v in str(value).split(",") if v != ""]
    if not values:
        raise CommandError("{} must be one or more numbers separated by commas".format(what))
    return values


def parse_polygon(args):
    """Parse positional tokens each shaped X,Y into a polygon point list."""
    if len(args) < 3:
        raise CommandError("a polygon needs at least 3 corners, each like X,Y")
    return [parse_point(a, "corner {}".format(i + 1)) for i, a in enumerate(args)]


def need_args(args, count, usage):
    if len(args) < count:
        raise CommandError("missing arguments. Usage: {}".format(usage))


def need_bay(session, name):
    bay = session.state.find_bay(name)
    if bay is None:
        names = ", ".join(b.name for b in session.state.bays) or "none yet"
        raise CommandError("no bay named {}. Bays: {}".format(name, names))
    return bay


def need_choice(value, choices, what):
    if value not in choices:
        raise CommandError("{} must be one of: {}. Got {!r}".format(
            what, ", ".join(choices), value))
    return value


def fmt(value):
    """Format a number for speech: drop trailing .0."""
    value = float(value)
    if value == int(value):
        return str(int(value))
    return "{:g}".format(value)
