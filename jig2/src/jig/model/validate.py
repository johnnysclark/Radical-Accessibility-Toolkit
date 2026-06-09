"""Semantic validation: findings beyond what dataclass construction enforces.

Returns a list of speakable finding strings; empty list means clean.
"""


def validate(state):
    findings = []
    findings += _check_names(state)
    for bay in state.bays:
        findings += _check_bay(bay)
        if state.site.boundary:
            findings += _check_bay_in_site(bay, state.site)
    return findings


def _check_names(state):
    findings = []
    seen = {}
    for kind, items in (("zone", state.zones), ("bay", state.bays)):
        for item in items:
            key = (kind, item.name)
            if key in seen:
                findings.append("duplicate {} name: {}".format(kind, item.name))
            seen[key] = True
    return findings


def _check_bay(bay):
    findings = []
    nx, ny = bay.counts
    for ap in bay.apertures:
        max_line = ny if ap.axis == "x" else nx
        if not (0 <= ap.line <= max_line):
            findings.append("bay {}: aperture {} is on line {} but lines run 0 to {}".format(
                bay.name, ap.id, ap.line, max_line))
        run = bay.width if ap.axis == "x" else bay.depth
        if ap.offset + ap.width > run:
            findings.append("bay {}: aperture {} ends at {:.1f} but the wall is {:.1f} long".format(
                bay.name, ap.id, ap.offset + ap.width, run))
    if bay.corridor:
        max_line = ny if bay.corridor.axis == "x" else nx
        if not (1 <= bay.corridor.line <= max_line - 1):
            findings.append("bay {}: corridor line {} must be an interior line, 1 to {}".format(
                bay.name, bay.corridor.line, max_line - 1))
    for cell in bay.cells:
        i, j = cell.at
        if not (0 <= i < nx and 0 <= j < ny):
            findings.append("bay {}: cell {} at {},{} is outside the {}x{} grid".format(
                bay.name, cell.name, i, j, nx, ny))
    seen = {}
    for cell in bay.cells:
        key = tuple(cell.at)
        if key in seen:
            findings.append("bay {}: two cells claim position {},{}".format(
                bay.name, key[0], key[1]))
        seen[key] = True
    return findings


def _check_bay_in_site(bay, site):
    from jig.geometry.bays import bay_corners
    xs = [p[0] for p in site.boundary]
    ys = [p[1] for p in site.boundary]
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    for cx, cy in bay_corners(bay):
        if not (min_x - 1e-9 <= cx <= max_x + 1e-9 and min_y - 1e-9 <= cy <= max_y + 1e-9):
            return ["bay {} extends outside the site bounds".format(bay.name)]
    return []
