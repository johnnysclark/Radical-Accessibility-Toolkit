"""JSON message formatting and response parsing for RhinoMCP socket protocol.

Matches the wire protocol of https://github.com/jingcheng-chen/rhinomcp
- Commands: {"type": "command_name", "params": {...}}
- Responses: {"status": "success|error", "result": {...}, "message": "..."}
- create_object params: {type, name, color, params: {geometry-specific}}
- Geometry types: POINT, LINE, POLYLINE, CIRCLE, ARC, ELLIPSE, CURVE, BOX, SPHERE, etc.
- Layer is set via get_or_set_current_layer before creating objects.
- Deletion via delete_object with id, name, or all=True.
"""

from __future__ import annotations

import json


def make_command(cmd_type: str, params: dict) -> bytes:
    """Format and encode a command for the RhinoMCP socket."""
    return json.dumps({"type": cmd_type, "params": params}).encode("utf-8") + b"\n"


def parse_response(buffer: str) -> tuple[dict | None, str]:
    """Try to parse a JSON response from buffer.

    Returns (response_dict, remaining_buffer). If no complete JSON found,
    returns (None, original_buffer).
    """
    depth = 0
    start = -1
    for i, ch in enumerate(buffer):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    obj = json.loads(buffer[start : i + 1])
                    return obj, buffer[i + 1 :]
                except json.JSONDecodeError:
                    continue
    return None, buffer


def set_layer_cmd(name: str) -> dict:
    """Build a command to set the current layer (objects created after this go on it)."""
    return {
        "type": "get_or_set_current_layer",
        "params": {"name": name},
    }


def create_polyline_cmd(
    points: list[tuple[float, float]],
    name: str,
    layer: str,
    color: tuple[int, int, int] = (0, 0, 0),
    closed: bool = True,
) -> list[dict]:
    """Build commands for a polyline: set layer, then create object.

    Returns a list of commands (set layer + create object).
    """
    pts_3d = [[p[0], p[1], 0] for p in points]
    if closed and pts_3d and pts_3d[0] != pts_3d[-1]:
        pts_3d.append(pts_3d[0])
    return [
        set_layer_cmd(layer),
        {
            "type": "create_object",
            "params": {
                "type": "POLYLINE",
                "name": name,
                "color": list(color),
                "params": {"points": pts_3d},
            },
        },
    ]


def create_line_cmd(
    start: tuple[float, float],
    end: tuple[float, float],
    layer: str,
    color: tuple[int, int, int] = (128, 128, 128),
) -> list[dict]:
    """Build commands for a line: set layer, then create object."""
    return [
        set_layer_cmd(layer),
        {
            "type": "create_object",
            "params": {
                "type": "LINE",
                "name": "",
                "color": list(color),
                "params": {
                    "start": [start[0], start[1], 0],
                    "end": [end[0], end[1], 0],
                },
            },
        },
    ]


def create_text_cmd(
    text: str,
    position: tuple[float, float],
    layer: str,
    height: float = 3.0,
) -> list[dict]:
    """Build commands for a text dot: set layer, then create point with name as label."""
    return [
        set_layer_cmd(layer),
        {
            "type": "create_object",
            "params": {
                "type": "POINT",
                "name": text,
                "params": {
                    "location": [position[0], position[1], 0],
                },
            },
        },
    ]


def create_layer_cmd(name: str, color: tuple[int, int, int] = (0, 0, 0)) -> dict:
    """Build a command to create a layer."""
    return {
        "type": "create_layer",
        "params": {
            "name": name,
            "color": list(color),
        },
    }


def delete_all_cmd() -> dict:
    """Build a command to delete all objects."""
    return {
        "type": "delete_object",
        "params": {"all": True},
    }


def delete_by_name_cmd(name: str) -> dict:
    """Build a command to delete an object by name."""
    return {
        "type": "delete_object",
        "params": {"name": name},
    }


def create_circle_cmd(
    center: tuple[float, float],
    radius: float,
    layer: str,
    color: tuple[int, int, int] = (128, 128, 128),
) -> list[dict]:
    """Build commands for a circle: set layer, then create object."""
    return [
        set_layer_cmd(layer),
        {
            "type": "create_object",
            "params": {
                "type": "CIRCLE",
                "name": "",
                "color": list(color),
                "params": {
                    "center": [center[0], center[1], 0],
                    "radius": radius,
                },
            },
        },
    ]


def execute_script_cmd(code: str) -> dict:
    """Build a command to execute a RhinoPython script in Rhino."""
    return {
        "type": "execute_rhinoscript_python_code",
        "params": {"code": code},
    }
