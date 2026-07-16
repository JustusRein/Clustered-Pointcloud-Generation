from OCP.BRepMesh import BRepMesh_IncrementalMesh



def triangulate(shape, tolerance):

    mesh = BRepMesh_IncrementalMesh(
        shape,
        tolerance,
        True,
        0.5,
        True
    )

    mesh.Perform()

    return shape