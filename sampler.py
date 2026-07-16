import numpy as np

from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE

from OCP.TopoDS import TopoDS

from OCP.BRep import BRep_Tool

from OCP.TopLoc import TopLoc_Location



def random_point_on_triangle(a,b,c):

    r1=np.random.random()
    r2=np.random.random()


    if r1+r2 > 1:

        r1=1-r1
        r2=1-r2


    return (
        a
        +
        r1*(b-a)
        +
        r2*(c-a)
    )



def triangle_area(a,b,c):

    return (
        0.5 *
        np.linalg.norm(
            np.cross(
                b-a,
                c-a
            )
        )
    )



def sample_shape(
        shape,
        spacing=1.0
):

    points=[]


    explorer=TopExp_Explorer(
        shape,
        TopAbs_FACE
    )


    while explorer.More():


        face=TopoDS.Face_s(
            explorer.Current()
        )


        location=TopLoc_Location()


        tri=(
            BRep_Tool.Triangulation_s(
                face,
                location
            )
        )


        if tri:


            nodes=[]


            for i in range(
                1,
                tri.NbNodes()+1
            ):

                p=tri.Node(i)

                nodes.append(
                    np.array(
                    [
                    p.X(),
                    p.Y(),
                    p.Z()
                    ]
                    )
                )



            triangles=tri.Triangles()



            for i in range(
                1,
                tri.NbTriangles()+1
            ):


                t=tri.Triangle(i)


                ia,ib,ic=(
                    t.Get()
                )


                a=nodes[ia-1]
                b=nodes[ib-1]
                c=nodes[ic-1]


                area=triangle_area(
                    a,b,c
                )


                # Anzahl Punkte nach Fläche
                n=max(
                    1,
                    int(
                    area /
                    (spacing**2)
                    )
                )


                for _ in range(n):

                    p=random_point_on_triangle(
                        a,b,c
                    )


                    points.append(
                        p
                    )


        explorer.Next()


    return np.array(points)
    
    
    
def voxel_sample(points, spacing):

    if len(points) == 0:
        return points

    grid = np.floor(
        points / spacing
    )

    _, idx = np.unique(
        grid,
        axis=0,
        return_index=True
    )

    return points[idx]