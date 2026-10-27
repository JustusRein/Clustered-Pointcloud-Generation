from __future__ import annotations

from pathlib import Path

import numpy as np
import open3d as o3d

from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopLoc import TopLoc_Location
from OCP.gp import gp_Trsf
from OCP.StlAPI import StlAPI_Writer


def save_cloud(cloud, filename) -> None:
    """Save a point cloud as PLY, PCD and XYZ."""
    filename = Path(filename)
    filename.parent.mkdir(parents=True, exist_ok=True)

    o3d.io.write_point_cloud(str(filename.with_suffix(".ply")), cloud)
    o3d.io.write_point_cloud(str(filename.with_suffix(".pcd")), cloud)
    np.savetxt(
        filename.with_suffix(".xyz"),
        np.asarray(cloud.points),
        fmt="%.8f",
    )


def _matrix_to_gp_trsf(matrix) -> gp_Trsf:
    """Convert the STEP reader's 4x4 homogeneous matrix to an OCCT transform."""
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (4, 4):
        raise ValueError(f"Expected a 4x4 placement matrix, got {matrix.shape}")
    if not np.isfinite(matrix).all():
        raise ValueError("Placement matrix contains NaN or infinite values")
    if not np.allclose(matrix[3], [0.0, 0.0, 0.0, 1.0], atol=1e-8):
        raise ValueError("Expected a homogeneous 4x4 transformation matrix")

    trsf = gp_Trsf()
    trsf.SetValues(
        float(matrix[0, 0]), float(matrix[0, 1]), float(matrix[0, 2]), float(matrix[0, 3]),
        float(matrix[1, 0]), float(matrix[1, 1]), float(matrix[1, 2]), float(matrix[1, 3]),
        float(matrix[2, 0]), float(matrix[2, 1]), float(matrix[2, 2]), float(matrix[2, 3]),
    )
    return trsf


def save_shape_stl(shape, location_matrix, filename, tolerance=0.1) -> Path:
    """Export a STEP part as STL in the same global frame as the point clouds.

    The STEP reader returns a shape and a separate global placement matrix.
    Some XCAF/OCCT shapes may also carry a top-level TopLoc_Location. Clear that
    top-level placement before applying the explicit matrix so that the assembly
    placement is not applied twice. If the shape already has identity location,
    this operation has no effect.
    """
    filename = Path(filename).with_suffix(".stl")
    filename.parent.mkdir(parents=True, exist_ok=True)

    # Use the same explicit part["location"] matrix as transform.apply_transform()
    # does for the point cloud. Do not retain a duplicate top-level shape location.
    local_shape = shape.Located(TopLoc_Location())
    trsf = _matrix_to_gp_trsf(location_matrix)
    transformed_shape = BRepBuilderAPI_Transform(local_shape, trsf, True).Shape()

    mesher = BRepMesh_IncrementalMesh(
        transformed_shape,
        float(tolerance),
        False,
        0.5,
        True,
    )
    mesher.Perform()

    writer = StlAPI_Writer()
    result = writer.Write(transformed_shape, str(filename))
    if result is False:
        raise RuntimeError(f"OpenCascade failed to write STL: {filename}")

    return filename


def save_triangle_mesh_stl(mesh, filename) -> Path:
    """Write a combined Open3D triangle mesh to an STL file."""
    filename = Path(filename).with_suffix(".stl")
    filename.parent.mkdir(parents=True, exist_ok=True)

    if mesh.is_empty() or len(mesh.triangles) == 0:
        raise ValueError(f"Cannot export an empty triangle mesh: {filename}")

    success = o3d.io.write_triangle_mesh(
        str(filename),
        mesh,
        write_ascii=False,
        compressed=False,
        print_progress=False,
    )
    if not success:
        raise RuntimeError(f"Open3D failed to write STL: {filename}")
    return filename
