"""ScenePlan -> .3dm via rhino3dm. Works offline; Rhino never needs to run.

Layer names like "JIG::Site" become a parent layer "JIG" with child "Site",
matching the layer tree the in-Rhino watcher creates with rs.AddLayer.
"""

import rhino3dm

from jig.geometry.compile import compile_scene
from jig.geometry.primitives import (Arc, Circle, Polyline, TextLabel,
                                     arc_three_points)


def export_3dm(state, path, style=None):
    plan = compile_scene(state, style)
    model = rhino3dm.File3dm()
    model.Settings.ModelUnitSystem = _unit_system(state.units)

    parent = rhino3dm.Layer()
    parent.Name = "JIG"
    parent_id = model.Layers[model.Layers.Add(parent)].Id

    total = 0
    for layer_name in sorted(plan):
        primitives = plan[layer_name]
        if not primitives:
            continue
        child = rhino3dm.Layer()
        child.Name = layer_name.split("::", 1)[-1]
        child.ParentLayerId = parent_id
        attributes = rhino3dm.ObjectAttributes()
        attributes.LayerIndex = model.Layers.Add(child)
        for primitive in primitives:
            _add(model, primitive, attributes)
            total += 1

    if not model.Write(path, 8):
        raise IOError("could not write {}".format(path))
    return total


def _add(model, primitive, attributes):
    if isinstance(primitive, Polyline):
        points = [rhino3dm.Point3d(x, y, 0.0) for x, y in primitive.points]
        if primitive.closed:
            points.append(points[0])
        model.Objects.AddPolyline(points, attributes)
    elif isinstance(primitive, Circle):
        center = rhino3dm.Point3d(primitive.center[0], primitive.center[1], 0.0)
        model.Objects.AddCircle(rhino3dm.Circle(center, primitive.radius), attributes)
    elif isinstance(primitive, Arc):
        start, mid, end = arc_three_points(primitive)
        arc = rhino3dm.Arc(rhino3dm.Point3d(start[0], start[1], 0.0),
                           rhino3dm.Point3d(mid[0], mid[1], 0.0),
                           rhino3dm.Point3d(end[0], end[1], 0.0))
        model.Objects.AddArc(arc, attributes)
    elif isinstance(primitive, TextLabel):
        location = rhino3dm.Point3d(primitive.at[0], primitive.at[1], 0.0)
        model.Objects.AddTextDot(primitive.text, location, attributes)
    else:
        raise TypeError("unknown primitive {!r}".format(primitive))


def _unit_system(units):
    mapping = {
        "feet": rhino3dm.UnitSystem.Feet,
        "meters": rhino3dm.UnitSystem.Meters,
        "inches": rhino3dm.UnitSystem.Inches,
        "millimeters": rhino3dm.UnitSystem.Millimeters,
    }
    return mapping.get(units, rhino3dm.UnitSystem.Feet)
