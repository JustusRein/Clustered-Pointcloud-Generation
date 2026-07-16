import open3d as o3d
import numpy as np



def create_cloud(points,id):


    cloud=o3d.geometry.PointCloud()


    cloud.points=(
        o3d.utility.Vector3dVector(
            points
        )
    )


    np.random.seed(id)


    cloud.paint_uniform_color(
        np.random.rand(3)
    )


    return cloud