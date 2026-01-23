import open3d as o3d


def load_ply_geometry(path: str) -> o3d.geometry.Geometry | None:
    """
    Load a .ply file as either a PointCloud or TriangleMesh.

    Returns:
        o3d.geometry.PointCloud | o3d.geometry.TriangleMesh | None
    """
    # PLY can be either a point cloud or a triangle mesh.
    # Prefer mesh when faces/triangles exist, otherwise fall back to point cloud.
    try:
        mesh = o3d.io.read_triangle_mesh(path)
        if mesh is not None and mesh.has_triangles():
            if not mesh.has_vertex_normals():
                mesh.compute_vertex_normals()
            return mesh
    except Exception:
        pass

    try:
        pcd = o3d.io.read_point_cloud(path)
        if pcd is not None and pcd.has_points():
            # Ensure it's visible even if the file has no colors.
            if not pcd.has_colors():
                pcd.paint_uniform_color([0.8, 0.8, 0.8])
            return pcd
    except Exception:
        pass

    return None

