import open3d as o3d
from pathlib import Path
import os
import glob


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


# 🎯 Suche nach allen .step-Dateien im Ordner "input"
step_files = glob.glob("input/*.step")

# 🎯 Sortiere nach Modifikationszeit (neueste zuerst)
step_files.sort(key=os.path.getmtime, reverse=True)

# 🎯 Nimm die erste Datei (die neueste)
if step_files:
    STEP_FILE = step_files[0]  # <-- das ist jetzt die neueste Datei
else:
    raise FileNotFoundError("Keine .step-Datei im Ordner 'input' gefunden!")



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


    filename = (OUTPUT_FOLDER + "/clusters/" + part["name"] + "_" + str(i))
    save_cloud(cloud, filename)

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