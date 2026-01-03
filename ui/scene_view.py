import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering


class SceneView:
    def __init__(self, window, bbox_origin=None, bbox_size=None):
        self.window = window
        self.widget = None
        self._geometry_name = "main_geometry"
        self._bbox_origin = np.array(bbox_origin) if bbox_origin is not None else np.array([0, 0, 0])
        self._bbox_size = np.array(bbox_size) if bbox_size is not None else np.array([1, 1, 1])
    

    def init(self, fov_deg=60):
        w = self.window
        self.widget = gui.SceneWidget()
        self.widget.scene = rendering.Open3DScene(w.renderer)
        self.widget.scene.show_skybox(False)
        self.widget.scene.set_lighting(
            self.widget.scene.LightingProfile.NO_SHADOWS, (0, 0, 0)
        )
        
        bbox = o3d.geometry.AxisAlignedBoundingBox(
            self._bbox_origin.tolist(), 
            (self._bbox_origin + self._bbox_size).tolist()
        )
        center = (self._bbox_origin + self._bbox_size / 2).tolist()
        self.widget.setup_camera(fov_deg, bbox, center)
    

    def add_geometry(self, geometry, name: str = None):
        if name is None:
            name = self._geometry_name
        material = rendering.MaterialRecord()
        self.widget.scene.add_geometry(name, geometry, material)
    

    def update_geometry(self, geometry, name: str = None):
        if name is None:
            name = self._geometry_name
        if self.widget.scene.has_geometry(name):
            self.widget.scene.remove_geometry(name)
        self.add_geometry(geometry, name)
    

    def remove_geometry(self, name: str = None):
        if name is None:
            name = self._geometry_name
        if self.widget.scene.has_geometry(name):
            self.widget.scene.remove_geometry(name)
    

    def setup_camera(self, fov_deg: float, bbox: o3d.geometry.AxisAlignedBoundingBox, 
                    center: list):
        self.widget.setup_camera(fov_deg, bbox, center)
    

    def fit_camera_to_geometry(self, geometry, fov_deg=60):
        bbox = geometry.get_axis_aligned_bounding_box()
        center = bbox.get_center()
        self.widget.setup_camera(fov_deg, bbox, center.tolist())
    

    def set_bounding_box(self, origin, size):
        self._bbox_origin = np.array(origin)
        self._bbox_size = np.array(size)
