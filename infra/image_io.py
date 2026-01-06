import open3d as o3d


def save_image(path, image):
    quality = 9 if path.endswith(".png") else 100
    o3d.io.write_image(path, image, quality)
