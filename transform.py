import numpy as np



def apply_transform(points,matrix):


    if len(points)==0:
        return points


    M=np.array(matrix)


    p=np.ones(
        (len(points),4)
    )


    p[:,:3]=points


    result=(
        M @ p.T
    ).T


    return result[:,:3]