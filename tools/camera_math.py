import numpy as np


GL2CV = np.array([
    [1, 0, 0, 0],
    [0,-1, 0, 0],
    [0, 0,-1, 0],
    [0, 0, 0, 1],
], dtype=np.float64)


def to_o3d_extrinsic_from_c2w(c2w: np.ndarray) -> np.ndarray:
    """
    Convert camera-to-world (OpenGL-style) to Open3D world-to-camera extrinsic.
    Suitable for Open3D visualization and ViewControl.
    """
    return GL2CV @ np.linalg.inv(c2w)


def create_camera_intrinsic_from_size(width=1024, height=768, hfov=60.0, vfov=60.0):
    fx = (width / 2.0)  / np.tan(np.radians(hfov)/2)
    fy = (height / 2.0)  / np.tan(np.radians(vfov)/2)
    fx = fy # not sure why, but it looks like fx should be governed/limited by fy
    return np.array(
        [[fx, 0, width / 2.0],
         [0, fy, height / 2.0],
         [0, 0,  1]])
