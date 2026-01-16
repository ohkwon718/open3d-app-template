import numpy as np
import open3d as o3d
from tools.camera_math import create_camera_intrinsic_from_size

def create_o3d_intrinsic(size):
    intrinsic = create_camera_intrinsic_from_size(size[0], size[1])
    return o3d.camera.PinholeCameraIntrinsic(width=size[0], height=size[1], fx=intrinsic[0][0], fy=intrinsic[1][1], cx=intrinsic[0][2], cy=intrinsic[1][2])


def create_camera_geometry(intrinsic: o3d.camera.PinholeCameraIntrinsic, extrinsic: np.ndarray, 
            img: np.ndarray = None, cam_color: np.ndarray = None, 
            O3DVisualizer: bool = False, scale: float = 1.0) -> list[o3d.geometry]:
    """Create camera frustum and optionally an image plane geometry."""
    # Create a LineSet object to visualize the camera frustum    
    cam_lineset = o3d.geometry.LineSet.create_camera_visualization(intrinsic, extrinsic)
    cam_lineset.lines = o3d.utility.Vector2iVector(np.asarray(cam_lineset.lines)[:8])
    cam_lineset.colors = o3d.utility.Vector3dVector(np.asarray(cam_lineset.colors)[:8])
    if cam_color is not None:
        line_colors = [cam_color for i in range(len(cam_lineset.lines))]
        cam_lineset.colors = o3d.utility.Vector3dVector(line_colors)
    cam_lineset.scale(scale, center=np.array(cam_lineset.points)[0])
    geometries = [cam_lineset]    
    if img is not None:        
        # Create a texture from the image
        tex = o3d.geometry.Image(img)
        # Create a rectangle mesh and map the texture onto it
        rectangle = o3d.geometry.TriangleMesh.create_box(width=1, height=1, depth=0.1, create_uv_map=True, map_texture_to_each_face=True)
        rectangle.triangles = o3d.utility.Vector3iVector([[0, 1, 2], [0, 2, 3]])
        rectangle.vertices = o3d.utility.Vector3dVector(np.array(cam_lineset.points)[1:])

        rectangle.triangle_material_ids = o3d.utility.IntVector(np.zeros(2, dtype=np.int32))
        if O3DVisualizer:
            rectangle.triangle_uvs = o3d.utility.Vector2dVector(np.array([[0, 1], [1, 1], [1, 0], [0, 1], [1, 0], [0, 0]]))            
            rectangle.paint_uniform_color([1.0, 1.0, 1.0])
            rectangle = o3d.t.geometry.TriangleMesh.from_legacy(rectangle)        
            material = o3d.visualization.Material('defaultUnlit')
            material.texture_maps['albedo'] = o3d.t.geometry.Image.from_legacy(tex)                
            rectangle.material = material        
        else:
            # visualize the texture on the both sides of the rectangle
            rectangle.textures = [tex, tex]        
            rectangle.triangle_uvs = o3d.utility.Vector2dVector(np.array([[0, 0], [1, 0], [1, 1], [0, 0], [1, 1], [0, 1]]))
            rectangle.triangle_material_ids = o3d.utility.IntVector(np.array([0, 0, 0, 1, 1, 1], dtype=np.int32))
        geometries.append(rectangle)    
    return geometries
