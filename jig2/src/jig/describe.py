"""State -> prose. Short labeled lines, predictable order, screen-reader first.

Shared by the CLI describe command, the text exporter, and the MCP
jig://describe resource.
"""

from jig.commands.util import fmt


def describe(state, section="all"):
    sections = {
        "meta": _meta,
        "site": _site,
        "zones": _zones,
        "grid": _grid,
        "bays": _bays,
    }
    if section != "all":
        key = section.lower().rstrip("s") + "s" if section.lower() in ("zone", "bay") else section.lower()
        if key not in sections:
            return "unknown section {}. Sections: {}".format(
                section, ", ".join(["all"] + list(sections)))
        return sections[key](state)
    return "\n".join(filter(None, (fn(state) for fn in sections.values())))


def _meta(state):
    return "model: {}. units: {}. modified: {}.".format(
        state.meta.name, state.units, state.meta.modified or "never")


def _site(state):
    if not state.site.boundary:
        return "site: not set."
    return "site: {} corners, {} by {} {}.".format(
        len(state.site.boundary), fmt(state.site.width),
        fmt(state.site.depth), state.units)


def _zones(state):
    if not state.zones:
        return "zones: none."
    lines = ["zones: {}.".format(len(state.zones))]
    for z in state.zones:
        lines.append("  zone {}: {} kind, {} corners, label {}.".format(
            z.name, z.kind, len(z.boundary), z.label))
    return "\n".join(lines)


def _grid(state):
    g = state.grid
    if not g.enabled:
        return "grid: off."
    return "grid: on, spacing {} by {}, rotation {} degrees.".format(
        fmt(g.spacing[0]), fmt(g.spacing[1]), fmt(g.rotation_deg))


def _bays(state):
    if not state.bays:
        return "bays: none."
    lines = ["bays: {}.".format(len(state.bays))]
    for b in state.bays:
        lines.append(describe_bay(b, state.units))
    return "\n".join(lines)


def describe_bay(bay, units="feet"):
    nx, ny = bay.counts
    lines = ["  bay {}: {} by {} bays, {} by {} {}, at {},{}, rotation {} degrees.".format(
        bay.name, nx, ny, fmt(bay.width), fmt(bay.depth), units,
        fmt(bay.origin[0]), fmt(bay.origin[1]), fmt(bay.rotation_deg))]
    lines.append("    columns: {}. walls: {}.".format(
        (nx + 1) * (ny + 1),
        "on, thickness {}".format(fmt(bay.walls.thickness)) if bay.walls.enabled else "off"))
    if bay.corridor:
        c = bay.corridor
        lines.append("    corridor: axis {}, line {}, width {}.".format(
            c.axis, c.line, fmt(c.width)))
    for ap in bay.apertures:
        detail = ", hinge {}, swings {}".format(ap.hinge, ap.swing) if ap.kind == "door" else ""
        lines.append("    {} {}: axis {} line {}, offset {}, width {}{}.".format(
            ap.kind, ap.id, ap.axis, ap.line, fmt(ap.offset), fmt(ap.width), detail))
    for cell in sorted(bay.cells, key=lambda c: (c.at[1], c.at[0])):
        lines.append("    cell {},{}: {}.".format(cell.at[0], cell.at[1], cell.name))
    for void in bay.voids:
        lines.append("    void {}: {} at {},{}, size {} by {}.".format(
            void.id, void.shape, fmt(void.center[0]), fmt(void.center[1]),
            fmt(void.size[0]), fmt(void.size[1])))
    return "\n".join(lines)


def status(state):
    parts = []
    parts.append("site set" if state.site.boundary else "no site")
    parts.append("{} zones".format(len(state.zones)))
    parts.append("{} bays".format(len(state.bays)))
    apertures = sum(len(b.apertures) for b in state.bays)
    if apertures:
        parts.append("{} apertures".format(apertures))
    cells = sum(len(b.cells) for b in state.bays)
    if cells:
        parts.append("{} named cells".format(cells))
    parts.append("grid on" if state.grid.enabled else "grid off")
    return ", ".join(parts)
