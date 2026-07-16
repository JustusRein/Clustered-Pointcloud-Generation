import open3d as o3d
from pathlib import Path


from config import *

from step_reader import load_step_assembly

from triangulation import triangulate

from sampler import (
    sample_shape,
    voxel_sample
)

from transform import apply_transform

from cloud import create_cloud

from exporter import save_cloud



STEP_FILE="input/baugruppe.step"



assembly=o3d.geometry.PointCloud()


parts=load_step_assembly(
    STEP_FILE
)



for i,part in enumerate(parts):


    print(
        "Teil:",
        part["name"]
    )


    triangulate(
        part["shape"],
        MESH_TOLERANCE
    )

    
    points=sample_shape(
        part["shape"],
        POINT_SPACING
    )


    points=voxel_sample(
        points,
        POINT_SPACING
    )


    points=apply_transform(
        points,
        part["location"]
    )


    cloud=create_cloud(
        points,
        i
    )


    assembly += cloud



    filename=(
        OUTPUT_FOLDER+
        "/clusters/"+
        part["name"]
    )


    save_cloud(
        cloud,
        filename
    )



save_cloud(
    assembly,
    OUTPUT_FOLDER+"/assembly"
)



print(
    "Fertig"
)