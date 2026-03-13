"""Export rendered views to PNG, PIAF PDF, and binary STL for 3D printing."""

from __future__ import annotations

import math
import os
import struct

from PIL import Image


def export_png(image: Image.Image, output_path: str) -> str:
    """Save a PIL image as PNG.

    Args:
        image: PIL Image to save.
        output_path: Destination file path.

    Returns:
        Absolute path to the saved file.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    image.save(output_path, "PNG")
    return os.path.abspath(output_path)


def export_piaf(image: Image.Image, output_path: str, paper_size: str = "letter") -> str:
    """Save a PIL image as a PIAF-ready tactile PDF.

    Requires tactile-core to be installed (pip install tactile-core).

    Args:
        image: PIL Image (ideally mode '1' or 'L').
        output_path: Destination PDF file path.
        paper_size: 'letter' or 'tabloid'.

    Returns:
        Absolute path to the saved file.

    Raises:
        ImportError: If tactile-core is not installed.
    """
    try:
        from tactile_core.core.pdf_generator import PIAFPDFGenerator
    except ImportError:
        raise ImportError(
            "PIAF export requires tactile-core. Install with: "
            "pip install -e tools/tact"
        )

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Ensure 1-bit image for PIAF
    if image.mode != "1":
        image = image.convert("1")

    generator = PIAFPDFGenerator()
    generator.generate(image, output_path, paper_size=paper_size)
    return os.path.abspath(output_path)


# ── STL Export for 3D Printing ────────────────────────────────


def _tri_normal(p0, p1, p2):
    """Compute outward normal from triangle winding (right-hand rule)."""
    ax, ay, az = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    bx, by, bz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
    nx = ay * bz - az * by
    ny = az * bx - ax * bz
    nz = ax * by - ay * bx
    mag = math.sqrt(nx * nx + ny * ny + nz * nz)
    if mag < 1e-12:
        return (0.0, 0.0, 1.0)
    return (nx / mag, ny / mag, nz / mag)


def _extract_mesh_triangles(file3dm, scale: float = 1.0, layer: str | None = None):
    """Extract triangles from all mesh and brep geometry in a 3dm file.

    Args:
        file3dm: rhino3dm.File3dm object.
        scale: Uniform scale factor applied to all vertices.
        layer: Optional layer name filter.

    Returns:
        List of (normal, v0, v1, v2) tuples where each vertex is (x, y, z).
    """
    triangles = []

    for obj in file3dm.Objects:
        geo = obj.Geometry
        if geo is None:
            continue

        # Layer filter
        if layer is not None:
            try:
                obj_layer = file3dm.Layers[obj.Attributes.LayerIndex].Name
            except (IndexError, Exception):
                obj_layer = ""
            if obj_layer.lower() != layer.lower():
                continue

        type_name = type(geo).__name__
        meshes_to_process = []

        # Direct meshes
        if "Mesh" in type_name and hasattr(geo, "Vertices") and hasattr(geo, "Faces"):
            meshes_to_process.append(geo)

        # Breps — get render meshes
        elif "Brep" in type_name:
            try:
                import rhino3dm
                brep_meshes = rhino3dm.MeshingParameters.FastRenderMesh
                # Try to get meshes from brep faces
                for fi in range(len(geo.Faces)):
                    mesh = geo.Faces[fi].GetMesh(rhino3dm.MeshType.Any)
                    if mesh is not None:
                        meshes_to_process.append(mesh)
            except Exception:
                pass

        # Extrusions — convert to brep then mesh
        elif "Extrusion" in type_name:
            try:
                brep = geo.ToBrep()
                if brep is not None:
                    import rhino3dm
                    for fi in range(len(brep.Faces)):
                        mesh = brep.Faces[fi].GetMesh(rhino3dm.MeshType.Any)
                        if mesh is not None:
                            meshes_to_process.append(mesh)
            except Exception:
                pass

        # Process all collected meshes
        for mesh in meshes_to_process:
            verts = mesh.Vertices
            faces = mesh.Faces
            for fi in range(len(faces)):
                face = faces[fi]
                # Triangle
                v0 = verts[face[0]]
                v1 = verts[face[1]]
                v2 = verts[face[2]]
                p0 = (v0.X * scale, v0.Y * scale, v0.Z * scale)
                p1 = (v1.X * scale, v1.Y * scale, v1.Z * scale)
                p2 = (v2.X * scale, v2.Y * scale, v2.Z * scale)
                normal = _tri_normal(p0, p1, p2)
                triangles.append((normal, p0, p1, p2))

                # Quad face — second triangle
                if face[3] != face[2]:
                    v3 = verts[face[3]]
                    p3 = (v3.X * scale, v3.Y * scale, v3.Z * scale)
                    normal2 = _tri_normal(p0, p2, p3)
                    triangles.append((normal2, p0, p2, p3))

    return triangles


def _write_binary_stl(triangles, filepath):
    """Write triangles as a binary STL file.

    Binary STL format:
      80 bytes  header
       4 bytes  uint32 triangle count
      per triangle:
        12 bytes  normal  (3 x float32)
        12 bytes  vertex0 (3 x float32)
        12 bytes  vertex1 (3 x float32)
        12 bytes  vertex2 (3 x float32)
         2 bytes  attribute count (0)
    """
    folder = os.path.dirname(os.path.abspath(filepath))
    if folder:
        os.makedirs(folder, exist_ok=True)

    with open(filepath, "wb") as f:
        header = b"model-reader STL export" + b"\0" * 57
        f.write(header[:80])
        f.write(struct.pack("<I", len(triangles)))
        for normal, v0, v1, v2 in triangles:
            f.write(struct.pack("<fff", *normal))
            f.write(struct.pack("<fff", *v0))
            f.write(struct.pack("<fff", *v1))
            f.write(struct.pack("<fff", *v2))
            f.write(struct.pack("<H", 0))

    return len(triangles)


def export_stl(
    file3dm,
    output_path: str,
    scale: float = 1.0,
    layer: str | None = None,
) -> tuple[str, int]:
    """Export 3dm geometry as a binary STL file for 3D printing.

    Extracts mesh triangles from all mesh, brep, and extrusion geometry.
    If the model has no mesh data, curves are skipped (STL is mesh-only).

    Args:
        file3dm: rhino3dm.File3dm object.
        output_path: Destination .stl file path.
        scale: Uniform scale factor (e.g. 25.4 to convert inches to mm).
        layer: Optional layer name — only export geometry on this layer.

    Returns:
        Tuple of (absolute_path, triangle_count).

    Raises:
        ValueError: If no mesh geometry is found.
    """
    triangles = _extract_mesh_triangles(file3dm, scale=scale, layer=layer)

    if not triangles:
        raise ValueError(
            "No mesh geometry found for STL export. "
            "The .3dm file may contain only curves/lines. "
            "STL requires mesh or brep surfaces."
        )

    count = _write_binary_stl(triangles, output_path)
    return (os.path.abspath(output_path), count)
