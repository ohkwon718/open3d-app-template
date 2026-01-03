import numpy as np


def generate_point_cloud_data(count: int = 1000, size: float = 1.0):
    points = np.random.uniform(-size/2, size/2, (count, 3))
    colors = (points - points.min(axis=0)) / (points.max(axis=0) - points.min(axis=0) + 1e-8)
    colors = np.clip(colors, 0, 1)
    return points, colors
