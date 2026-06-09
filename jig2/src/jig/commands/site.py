"""Site commands."""

from jig.commands.registry import command
from jig.commands.util import fmt, need_args, parse_polygon, to_float
from jig.model.schema import Site


@command("site set", "site set WIDTH DEPTH",
         "Set a rectangular site boundary with its corner at 0,0.")
def site_set(session, args, flags):
    need_args(args, 2, "site set WIDTH DEPTH")
    w = to_float(args[0], "width")
    d = to_float(args[1], "depth")
    session.state.site = Site(boundary=[[0, 0], [w, 0], [w, d], [0, d]])
    return "site set to {} by {} {}".format(fmt(w), fmt(d), session.state.units)


@command("site polygon", "site polygon X,Y X,Y X,Y ...",
         "Set a polygonal site boundary from corner points.")
def site_polygon(session, args, flags):
    boundary = parse_polygon(args)
    session.state.site = Site(boundary=boundary)
    return "site set to a {}-corner polygon, {} by {} {}".format(
        len(boundary), fmt(session.state.site.width),
        fmt(session.state.site.depth), session.state.units)


@command("site clear", "site clear", "Remove the site boundary.")
def site_clear(session, args, flags):
    session.state.site = Site()
    return "site boundary removed"
