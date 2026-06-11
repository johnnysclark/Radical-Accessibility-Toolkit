"""Text command grammar, shared by the CLI and the chat REPL.

One sentence in, one op dict out. Sentences are designed to be spoken:
    box 10 10 30 at 0,0,0 name "tower base"
    move m17 by 0,0,10
    difference "tower base" minus m4 m5
Coordinates are comma-joined numbers with no spaces (x,y or x,y,z).
Object references are ids (m17), quoted names ("tower base"), or the
word last. Every op accepts trailing clauses: name "..." and
layer "...". Errors always answer with the usage line.
"""

from __future__ import annotations

import shlex

USAGE = {
    "point": 'point X,Y[,Z]',
    "line": 'line X,Y[,Z] to X,Y[,Z]',
    "polyline": 'polyline P1 P2 P3 ... [closed]',
    "circle": 'circle radius R [at X,Y[,Z]]',
    "arc": 'arc P1 P2 P3',
    "rect": 'rect WIDTH DEPTH [at X,Y[,Z]]',
    "curve": 'curve P1 P2 P3 ... [degree N]',
    "text": 'text "WORDS" at X,Y[,Z] [height H]',
    "box": 'box WIDTH DEPTH HEIGHT [at X,Y,Z]',
    "sphere": 'sphere radius R [at X,Y,Z]',
    "cylinder": 'cylinder radius R height H [at X,Y,Z]',
    "cone": 'cone radius R height H [at X,Y,Z]',
    "extrude": 'extrude OBJECT height H, or: extrude OBJECT by X,Y,Z',
    "loft": 'loft OBJECT OBJECT ...',
    "revolve": 'revolve OBJECT axis X,Y,Z to X,Y,Z [angle A]',
    "union": 'union OBJECT OBJECT ...',
    "difference": 'difference KEEP ... minus CUT ...',
    "intersect": 'intersect OBJECT OBJECT ...',
    "move": 'move OBJECTS by X,Y,Z',
    "rotate": 'rotate OBJECTS by ANGLE [around X,Y,Z] [axis x|y|z]',
    "scale": 'scale OBJECTS by FACTOR [around X,Y,Z]',
    "mirror": 'mirror OBJECTS across X,Y to X,Y',
    "copy": 'copy OBJECTS by X,Y,Z [count N]',
    "delete": 'delete OBJECTS, or: delete all',
    "rename": 'rename OBJECT "NEW NAME"',
    "layer": 'layer add NAME',
    "put": 'put OBJECTS on LAYER',
    "group": 'group OBJECTS [name "NAME"]',
    "ungroup": 'ungroup GROUP',
}

ALIASES = {
    "rectangle": "rect",
    "subtract": "difference",
    "intersection": "intersect",
    "poly": "polyline",
}

OP_WORDS = set(USAGE) | set(ALIASES)


class GrammarError(Exception):
    pass


def is_command(text: str) -> bool:
    """True when the first word is a grammar op word."""
    first = text.strip().split(" ", 1)[0].lower() if text.strip() else ""
    return first in OP_WORDS


def parse(text: str) -> dict:
    """Parse one sentence into an op dict {op, params, name?, layer?}."""
    try:
        tokens = shlex.split(text, posix=True)
    except ValueError as exc:
        raise GrammarError("could not read that: {0}".format(exc))
    return parse_tokens(tokens)


def parse_tokens(tokens: list[str]) -> dict:
    """Parse pre-split tokens (the CLI passes argv straight through)."""
    if not tokens:
        raise GrammarError("empty command")
    word = ALIASES.get(tokens[0].lower(), tokens[0].lower())
    if word not in USAGE:
        raise GrammarError(
            "unknown command {0!r}. Known commands: {1}".format(
                tokens[0], ", ".join(sorted(USAGE))))
    stream = _Stream(word, tokens[1:], " ".join(tokens))
    name, layer = stream.extract_clauses()
    parser = _PARSERS[word]
    op_dict = parser(stream)
    stream.expect_done()
    if name:
        op_dict["name"] = name
    if layer:
        op_dict["layer"] = layer
    return op_dict


# -- token stream ----------------------------------------------------------


def _is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def _is_coord(token: str) -> bool:
    parts = token.split(",")
    return len(parts) in (2, 3) and all(_is_number(p) for p in parts if p != "") \
        and "" not in parts


class _Stream:
    def __init__(self, word: str, tokens: list[str], raw: str):
        self.word = word
        self.tokens = tokens
        self.raw = raw
        self.pos = 0

    def fail(self, why: str = "") -> GrammarError:
        message = "usage: " + USAGE[self.word]
        if why:
            message = why + ". " + message
        return GrammarError(message)

    def extract_clauses(self) -> tuple[str | None, str | None]:
        """Pull trailing name "..." and layer "..." clauses out, anywhere."""
        name = layer = None
        kept = []
        index = 0
        while index < len(self.tokens):
            token = self.tokens[index].lower()
            # "layer add NAME" is the layer command itself, not a clause.
            is_clause = (token in ("name", "layer")
                         and not (self.word == "layer" and index == 0)
                         and index + 1 < len(self.tokens))
            if is_clause:
                value = self.tokens[index + 1]
                if token == "name":
                    name = value
                else:
                    layer = value
                index += 2
            else:
                kept.append(self.tokens[index])
                index += 1
        self.tokens = kept
        return name, layer

    def done(self) -> bool:
        return self.pos >= len(self.tokens)

    def peek(self) -> str | None:
        return self.tokens[self.pos] if not self.done() else None

    def take(self) -> str:
        if self.done():
            raise self.fail("missing words at the end")
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def take_word(self, word: str) -> None:
        token = self.take()
        if token.lower() != word:
            raise self.fail("expected the word {0!r}, got {1!r}".format(word, token))

    def opt_word(self, word: str) -> bool:
        if not self.done() and self.peek().lower() == word:
            self.pos += 1
            return True
        return False

    def number(self, label: str) -> float:
        token = self.take()
        if not _is_number(token):
            raise self.fail("{0} must be a number, got {1!r}".format(label, token))
        return float(token)

    def integer(self, label: str) -> int:
        return int(self.number(label))

    def coord(self, label: str) -> list[float]:
        token = self.take()
        if not _is_coord(token):
            raise self.fail(
                "{0} must look like X,Y or X,Y,Z with no spaces, got {1!r}".format(
                    label, token))
        parts = [float(p) for p in token.split(",")]
        if len(parts) == 2:
            parts.append(0.0)
        return parts

    def coords(self, minimum: int, label: str) -> list[list[float]]:
        points = []
        while not self.done() and _is_coord(self.peek()):
            points.append(self.coord(label))
        if len(points) < minimum:
            raise self.fail("{0} needs at least {1} points".format(label, minimum))
        return points

    def refs(self, label: str, stop_words: tuple = ()) -> list[str]:
        """Object references until a keyword: ids, quoted names, or last."""
        out = []
        while not self.done():
            token = self.peek()
            if token.lower() in stop_words or token.lower() in _KEYWORDS:
                break
            out.append(self.take())
        if not out:
            raise self.fail("say which objects, like m3, or a quoted name, "
                            "or last ({0})".format(label))
        return out

    def expect_done(self) -> None:
        if not self.done():
            raise self.fail("did not understand {0!r}".format(self.peek()))


_KEYWORDS = {"at", "by", "to", "radius", "height", "angle", "axis", "around",
             "count", "degree", "closed", "minus", "across", "on", "name",
             "layer", "plane", "normal", "center"}


# -- per-op parsers --------------------------------------------------------


def _p_point(s: _Stream) -> dict:
    s.opt_word("at")
    return {"op": "create_point", "params": {"at": s.coord("the point")}}


def _p_line(s: _Stream) -> dict:
    start = s.coord("start")
    s.take_word("to")
    return {"op": "create_line",
            "params": {"start": start, "end": s.coord("end")}}


def _p_polyline(s: _Stream) -> dict:
    points = s.coords(2, "polyline")
    closed = s.opt_word("closed")
    return {"op": "create_polyline", "params": {"points": points, "closed": closed}}


def _p_circle(s: _Stream) -> dict:
    center, radius = [0.0, 0.0, 0.0], None
    while not s.done():
        if s.opt_word("radius"):
            radius = s.number("radius")
        elif s.opt_word("at") or s.opt_word("center"):
            center = s.coord("center")
        elif _is_number(s.peek() or ""):
            radius = s.number("radius")
        else:
            break
    if radius is None:
        raise s.fail("missing radius")
    return {"op": "create_circle", "params": {"center": center, "radius": radius}}


def _p_arc(s: _Stream) -> dict:
    p1, p2, p3 = s.coord("first point"), s.coord("second point"), s.coord("third point")
    return {"op": "create_arc", "params": {"p1": p1, "p2": p2, "p3": p3}}


def _p_rect(s: _Stream) -> dict:
    width, depth = s.number("width"), s.number("depth")
    corner = s.coord("corner") if s.opt_word("at") else [0.0, 0.0, 0.0]
    return {"op": "create_rectangle",
            "params": {"corner": corner, "width": width, "depth": depth}}


def _p_curve(s: _Stream) -> dict:
    points = s.coords(3, "curve")
    degree = s.integer("degree") if s.opt_word("degree") else 3
    return {"op": "create_curve", "params": {"points": points, "degree": degree}}


def _p_text(s: _Stream) -> dict:
    content = s.take()
    s.take_word("at")
    at = s.coord("position")
    height = s.number("height") if s.opt_word("height") else 1.0
    return {"op": "create_text",
            "params": {"text": content, "at": at, "height": height}}


def _p_box(s: _Stream) -> dict:
    size = [s.number("width"), s.number("depth"), s.number("height")]
    corner = s.coord("corner") if s.opt_word("at") else [0.0, 0.0, 0.0]
    return {"op": "create_box", "params": {"corner": corner, "size": size}}


def _p_sphere(s: _Stream) -> dict:
    s.opt_word("radius")
    radius = s.number("radius")
    center = s.coord("center") if s.opt_word("at") else [0.0, 0.0, 0.0]
    return {"op": "create_sphere", "params": {"center": center, "radius": radius}}


def _p_cylinder(s: _Stream) -> dict:
    return _radius_height(s, "create_cylinder")


def _p_cone(s: _Stream) -> dict:
    return _radius_height(s, "create_cone")


def _radius_height(s: _Stream, op: str) -> dict:
    s.opt_word("radius")
    radius = s.number("radius")
    s.opt_word("height")
    height = s.number("height")
    base = s.coord("base") if s.opt_word("at") else [0.0, 0.0, 0.0]
    return {"op": op,
            "params": {"base": base, "radius": radius, "height": height}}


def _p_extrude(s: _Stream) -> dict:
    source = s.refs("the curve to extrude")[0]
    if s.opt_word("by"):
        return {"op": "extrude", "params": {"source": source,
                                            "vector": s.coord("direction")}}
    s.opt_word("height")
    return {"op": "extrude", "params": {"source": source,
                                        "height": s.number("height")}}


def _p_loft(s: _Stream) -> dict:
    return {"op": "loft", "params": {"sources": s.refs("curves to loft")}}


def _p_revolve(s: _Stream) -> dict:
    source = s.refs("the curve to revolve")[0]
    s.take_word("axis")
    axis_start = s.coord("axis start")
    s.take_word("to")
    axis_end = s.coord("axis end")
    angle = s.number("angle") if s.opt_word("angle") else 360.0
    return {"op": "revolve", "params": {
        "source": source, "axis_start": axis_start,
        "axis_end": axis_end, "angle": angle}}


def _p_union(s: _Stream) -> dict:
    return {"op": "boolean_union", "params": {"inputs": s.refs("solids")}}


def _p_difference(s: _Stream) -> dict:
    keep = s.refs("what to keep", stop_words=("minus",))
    s.take_word("minus")
    cut = s.refs("what to cut away")
    return {"op": "boolean_difference", "params": {"keep": keep, "cut": cut}}


def _p_intersect(s: _Stream) -> dict:
    return {"op": "boolean_intersection", "params": {"inputs": s.refs("solids")}}


def _p_move(s: _Stream) -> dict:
    targets = s.refs("objects to move")
    s.opt_word("by")
    return {"op": "move", "params": {"ids": targets,
                                     "vector": s.coord("the move")}}


def _p_rotate(s: _Stream) -> dict:
    targets = s.refs("objects to rotate")
    s.take_word("by")
    angle = s.number("angle")
    center = axis = None
    while not s.done():
        if s.opt_word("around"):
            center = s.coord("center")
        elif s.opt_word("axis"):
            token = s.take().lower()
            named = {"x": [1, 0, 0], "y": [0, 1, 0], "z": [0, 0, 1]}
            if token in named:
                axis = named[token]
            elif _is_coord(token):
                axis = [float(p) for p in token.split(",")]
            else:
                raise s.fail("axis must be x, y, z, or X,Y,Z")
        else:
            break
    params = {"ids": targets, "angle": angle, "axis": axis or [0, 0, 1]}
    if center is not None:
        params["center"] = center
    return {"op": "rotate", "params": params}


def _p_scale(s: _Stream) -> dict:
    targets = s.refs("objects to scale")
    s.take_word("by")
    token = s.take()
    if _is_coord(token):
        factors = [float(p) for p in token.split(",")]
        if len(factors) == 2:
            factors.append(1.0)
    elif _is_number(token):
        factors = [float(token)] * 3
    else:
        raise s.fail("scale factor must be a number or FX,FY,FZ")
    params = {"ids": targets, "factors": factors}
    if s.opt_word("around"):
        params["center"] = s.coord("center")
    return {"op": "scale", "params": params}


def _p_mirror(s: _Stream) -> dict:
    targets = s.refs("objects to mirror")
    if s.opt_word("across"):
        p1 = s.coord("line start")
        s.take_word("to")
        p2 = s.coord("line end")
        direction = [p2[i] - p1[i] for i in range(3)]
        normal = [-direction[1], direction[0], 0.0]
        if normal == [0.0, 0.0, 0.0]:
            raise s.fail("mirror line start and end are the same point")
        return {"op": "mirror", "params": {
            "ids": targets, "plane_point": p1, "plane_normal": normal}}
    s.take_word("plane")
    plane_point = s.coord("plane point")
    s.take_word("normal")
    plane_normal = s.coord("plane normal")
    return {"op": "mirror", "params": {
        "ids": targets, "plane_point": plane_point,
        "plane_normal": plane_normal}}


def _p_copy(s: _Stream) -> dict:
    targets = s.refs("objects to copy")
    s.opt_word("by")
    vector = s.coord("the offset")
    count = s.integer("count") if s.opt_word("count") else 1
    return {"op": "copy", "params": {"ids": targets, "vector": vector,
                                     "count": count}}


def _p_delete(s: _Stream) -> dict:
    if s.opt_word("all"):
        return {"op": "delete", "params": {"all": True}}
    return {"op": "delete", "params": {"ids": s.refs("objects to delete")}}


def _p_rename(s: _Stream) -> dict:
    target = s.take()
    new_name = s.take()
    return {"op": "set_name", "params": {"id": target, "name": new_name}}


def _p_layer(s: _Stream) -> dict:
    s.take_word("add")
    return {"op": "create_layer", "params": {"name": s.take()}}


def _p_put(s: _Stream) -> dict:
    targets = s.refs("objects to move to a layer", stop_words=("on",))
    s.take_word("on")
    return {"op": "set_layer", "params": {"ids": targets, "layer": s.take()}}


def _p_group(s: _Stream) -> dict:
    return {"op": "group", "params": {"members": s.refs("objects to group")}}


def _p_ungroup(s: _Stream) -> dict:
    return {"op": "ungroup", "params": {"gid": s.take()}}


_PARSERS = {
    "point": _p_point, "line": _p_line, "polyline": _p_polyline,
    "circle": _p_circle, "arc": _p_arc, "rect": _p_rect, "curve": _p_curve,
    "text": _p_text, "box": _p_box, "sphere": _p_sphere,
    "cylinder": _p_cylinder, "cone": _p_cone, "extrude": _p_extrude,
    "loft": _p_loft, "revolve": _p_revolve, "union": _p_union,
    "difference": _p_difference, "intersect": _p_intersect, "move": _p_move,
    "rotate": _p_rotate, "scale": _p_scale, "mirror": _p_mirror,
    "copy": _p_copy, "delete": _p_delete, "rename": _p_rename,
    "layer": _p_layer, "put": _p_put, "group": _p_group,
    "ungroup": _p_ungroup,
}

assert set(_PARSERS) == set(USAGE), "every op word needs usage and a parser"


def help_lines() -> list[str]:
    lines = ["Commands you can say directly:"]
    for word in sorted(USAGE):
        lines.append("  " + USAGE[word])
    lines.append('References: ids like m3, quoted names like "tower base", or last.')
    lines.append('Every command also takes: name "..." and layer "...".')
    return lines
