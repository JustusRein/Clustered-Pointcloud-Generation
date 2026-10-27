from __future__ import annotations

import glob
import json
import os
from pathlib import Path

import open3d as o3d

from config import *
from step_reader import load_step_assembly
from triangulation import triangulate
from sampler import sample_shape, voxel_sample
from transform import apply_transform
from cloud import create_cloud
from exporter import save_cloud, save_shape_stl


def newest_step_file(input_folder: str = "input") -> Path:
    """Return the newest STEP file in the input folder."""
    candidates = []
    for pattern in ("*.step", "*.stp", "*.STEP", "*.STP"):
        candidates.extend(glob.glob(str(Path(input_folder) / pattern)))

    if not candidates:
        raise FileNotFoundError(
            f"No STEP assembly found in '{input_folder}'. "
            "Place a .step or .stp file there."
        )

    return Path(max(candidates, key=os.path.getmtime))


def main() -> None:
    step_file = newest_step_file()
    print(f"STEP assembly: {step_file}")

    output_root = Path(OUTPUT_FOLDER)
    clusters_dir = output_root / "clusters"
    stl_dir = output_root / "stl"
    clusters_dir.mkdir(parents=True, exist_ok=True)
    stl_dir.mkdir(parents=True, exist_ok=True)

    parts = load_step_assembly(str(step_file))
    if not parts:
        raise RuntimeError("No individual parts were found in the STEP assembly.")

    assembly_cloud = o3d.geometry.PointCloud()
    part_records = []

    for index, part in enumerate(parts):
        part_name = str(part.get("name") or "part")
        safe_name = "".join(
            c if c.isalnum() or c in ("-", "_", ".") else "_"
            for c in part_name
        ).strip("._") or "part"
        stem = f"{safe_name}_{index:04d}"

        print(f"[{index + 1}/{len(parts)}] Processing: {part_name}")

        # STL: reset any top-level shape placement and apply the same explicit
        # global matrix that the original point-cloud pipeline uses.
        stl_path = stl_dir / f"{stem}.stl"
        save_shape_stl(
            shape=part["shape"],
            location_matrix=part["location"],
            filename=stl_path,
            tolerance=float(MESH_TOLERANCE),
        )

        # Keep the original point-cloud placement logic unchanged.
        triangulate(part["shape"], MESH_TOLERANCE)
        points = sample_shape(part["shape"], POINT_SPACING)
        points = voxel_sample(points, POINT_SPACING)
        points = apply_transform(points, part["location"])
        cloud = create_cloud(points, index)

        save_cloud(cloud, clusters_dir / stem)
        assembly_cloud += cloud

        part_records.append(
            {
                "name": part_name,
                "stem": stem,
                "stl_path": str(stl_path),
                "cloud_stem": str(clusters_dir / stem),
            }
        )

    save_cloud(assembly_cloud, output_root / "assembly")

    metadata_path = output_root / "parts_manifest.json"
    metadata_path.write_text(
        json.dumps(part_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Parts exported: {len(parts)}")
    print(f"Individual STLs: {stl_dir}")
    print(f"Point clouds: {clusters_dir}")
    print(f"Manifest: {metadata_path}")
    print("Finished.")


if __name__ == "__main__":
    main()
