from pathlib import Path
import open3d as o3d
import numpy as np



def save_cloud(cloud, filename):

    filename = Path(filename)

    # kompletten Zielordner erstellen
    filename.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    o3d.io.write_point_cloud(
        str(filename.with_suffix(".ply")),
        cloud
    )


    o3d.io.write_point_cloud(
        str(filename.with_suffix(".pcd")),
        cloud
    )


    np.savetxt(
        filename.with_suffix(".xyz"),
        np.asarray(cloud.points)
    )