"""The declared support table must match what rhino3dm actually has.

If a rhino3dm upgrade removes or adds capability, this fails loudly
instead of surprising the user at modeling time.
"""

import pytest

rhino3dm = pytest.importorskip("rhino3dm")

from maquette import ops  # noqa: E402
from maquette.backends.headless import SUPPORT  # noqa: E402


def test_every_create_op_has_a_declared_support_level():
    assert set(SUPPORT) == set(ops.KINDS), \
        "every create-class op needs a support entry"


def test_declared_full_support_is_backed_by_rhino3dm():
    needed = {
        "create_point": [("Point3d",), ("Point",)],
        "create_line": [("LineCurve",)],
        "create_polyline": [("Polyline",)],
        "create_circle": [("Circle",)],
        "create_arc": [("Arc",)],
        "create_rectangle": [("Polyline",)],
        "create_curve": [("Curve", "CreateControlPointCurve")],
        "create_text": [("TextDot",)],
        "create_box": [("Box",), ("Brep", "CreateFromBox")],
        "create_sphere": [("Sphere",), ("Brep", "CreateFromSphere")],
        "create_cylinder": [("Cylinder",)],
        "create_cone": [("RevSurface", "Create"), ("Brep", "CreateFromRevSurface")],
        "extrude": [("Extrusion", "Create")],
        "revolve": [("RevSurface", "Create")],
    }
    for op, requirements in needed.items():
        assert SUPPORT[op] in ("full", "approx"), op
        for requirement in requirements:
            target = rhino3dm
            for attr in requirement:
                assert hasattr(target, attr), \
                    "{0} needs rhino3dm.{1}".format(op, ".".join(requirement))
                target = getattr(target, attr)


def test_compute_ops_are_declared_record_only():
    # rhino3dm has no solid booleans or lofts; if that ever changes,
    # upgrade the backend and this table together.
    for op in ("boolean_union", "boolean_difference", "boolean_intersection",
               "loft", "script"):
        assert SUPPORT[op] == "record", op


def test_transform_support():
    for method in ("Translation", "Rotation", "Scale", "Mirror"):
        assert hasattr(rhino3dm.Transform, method)
