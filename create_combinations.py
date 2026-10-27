from __future__ import annotations

import itertools
import json
from pathlib import Path

import open3d as o3d

from config import OUTPUT_FOLDER
from exporter import save_cloud, save_triangle_mesh_stl


def main() -> None:
    output_root = Path(OUTPUT_FOLDER)
    manifest_path = output_root / "parts_manifest.json"

    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing {manifest_path}. Run 'python main.py' first.")

    parts = json.loads(manifest_path.read_text(encoding="utf-8"))
    if len(parts) < 2:
        raise RuntimeError(
            f"Only {len(parts)} part(s) found in {manifest_path}; "
            "at least two parts are required to create combinations."
        )

    combinations_root = output_root / "combinations"
    stl_output = combinations_root / "stl"
    cloud_output = combinations_root / "pointclouds"
    stl_output.mkdir(parents=True, exist_ok=True)
    cloud_output.mkdir(parents=True, exist_ok=True)

    total_combinations = (2 ** len(parts)) - len(parts) - 1
    print(f"Found {len(parts)} parts.")
    print(f"Creating {total_combinations:,} combinations (sizes 2..{len(parts)}).")
    print(f"STL output: {stl_output.resolve()}")
    print(f"Point-cloud output: {cloud_output.resolve()}")

    cached = []
    for part in parts:
        stl_path = Path(part["stl_path"])
        cloud_stem = Path(part["cloud_stem"])
        pcd_path = cloud_stem.with_suffix(".pcd")

        mesh = o3d.io.read_triangle_mesh(str(stl_path))
        if mesh.is_empty() or len(mesh.triangles) == 0:
            raise RuntimeError(f"STL could not be loaded or contains no triangles: {stl_path}")

        cloud = o3d.io.read_point_cloud(str(pcd_path))
        if cloud.is_empty():
            raise RuntimeError(f"Point cloud could not be loaded or is empty: {pcd_path}")

        cached.append((part, mesh, cloud))

    combination_index = 0
    manifest_rows = []

    for size in range(2, len(cached) + 1):
        size_count = 0
        for selected_indices in itertools.combinations(range(len(cached)), size):
            combination_index += 1
            size_count += 1
            combo_id = f"combo_{combination_index:07d}_n{size}"

            combined_mesh = o3d.geometry.TriangleMesh()
            combined_cloud = o3d.geometry.PointCloud()
            selected_names = []

            for index in selected_indices:
                part, mesh, cloud = cached[index]
                # Inputs are already in the STEP assembly/global coordinates.
                # Never apply the placement matrices again here.
                combined_mesh += mesh
                combined_cloud += cloud
                selected_names.append(str(part.get("name", part["stem"])))

            combined_mesh.remove_duplicated_vertices()
            combined_mesh.remove_degenerate_triangles()
            combined_mesh.remove_duplicated_triangles()
            combined_mesh.remove_unreferenced_vertices()
            combined_mesh.compute_vertex_normals()

            save_triangle_mesh_stl(combined_mesh, stl_output / combo_id)
            save_cloud(combined_cloud, cloud_output / combo_id)

            manifest_rows.append(
                {
                    "combination_id": combo_id,
                    "size": size,
                    "parts": selected_names,
                    "stl": str((stl_output / f"{combo_id}.stl").as_posix()),
                    "pointcloud_stem": str((cloud_output / combo_id).as_posix()),
                }
            )

        print(f"Finished combinations with {size} parts: {size_count:,}")

    combo_manifest = combinations_root / "combinations_manifest.json"
    combo_manifest.write_text(
        json.dumps(manifest_rows, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Created {combination_index:,} combination STL files.")
    print(f"STL files: {stl_output.resolve()}")
    print(f"Manifest: {combo_manifest.resolve()}")


if __name__ == "__main__":
    main()
