import numpy as np


ToGLCamera = np.array([
    [1,  0,  0,  0],
    [0,  -1,  0,  0],
    [0,  0,  -1,  0],
    [0,  0,  0,  1]
])
FromGLGamera = np.linalg.inv(ToGLCamera)


def model_matrix_to_extrinsic_matrix(model_matrix):
    return np.linalg.inv(model_matrix @ FromGLGamera)


def create_camera_intrinsic_from_size(width=1024, height=768, hfov=60.0, vfov=60.0):
    fx = (width / 2.0)  / np.tan(np.radians(hfov)/2)
    fy = (height / 2.0)  / np.tan(np.radians(vfov)/2)
    fx = fy # not sure why, but it looks like fx should be governed/limited by fy
    return np.array(
        [[fx, 0, width / 2.0],
         [0, fy, height / 2.0],
         [0, 0,  1]])


