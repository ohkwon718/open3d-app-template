import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

from tools.camera_math import to_o3d_extrinsic_from_c2w, create_camera_intrinsic_from_size


class SceneWidget:
    def __init__(self, window, bbox_origin=None, bbox_size=None):
        self.window = window
        self.widget = None
        self._geometry_name = "main_geometry"
        self._bbox_origin = np.array(bbox_origin) if bbox_origin is not None else np.array([0, 0, 0])
        self._bbox_size = np.array(bbox_size) if bbox_size is not None else np.array([1, 1, 1])
        # Registry so UI can hide/show geometries without losing the geometry objects.
        self._geometries: dict[str, o3d.geometry.Geometry] = {}
        self._materials: dict[str, rendering.MaterialRecord] = {}
        self._visible: dict[str, bool] = {}


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

    def _make_material(self, geometry) -> rendering.MaterialRecord:
        material = rendering.MaterialRecord()
        # Make default visuals "just work" for typical template geometries.
        # - Point clouds should show per-point colors without relying on lighting.
        # - Colored meshes (e.g., coordinate frame) should also render with colors.
        if isinstance(geometry, o3d.geometry.PointCloud):
            material.shader = "defaultUnlit"
            material.point_size = 3.0
        elif isinstance(geometry, o3d.geometry.LineSet):
            # Camera frustums etc.
            material.shader = "unlitLine"
            material.line_width = 2.0
        elif isinstance(geometry, o3d.geometry.TriangleMesh) and geometry.has_vertex_colors():
            material.shader = "defaultUnlit"
        return material

    def _add_to_scene(self, name: str):
        geometry = self._geometries.get(name)
        material = self._materials.get(name)
        if geometry is None or material is None:
            return
        self.widget.scene.add_geometry(name, geometry, material)


    def add_geometry(self, geometry, name: str = None):
        if name is None:
            name = self._geometry_name
        self._geometries[name] = geometry
        self._materials[name] = self._make_material(geometry)
        if name not in self._visible:
            self._visible[name] = True
        if self._visible.get(name, True):
            self._add_to_scene(name)


    def update_geometry(self, geometry, name: str = None):
        if name is None:
            name = self._geometry_name
        # Preserve visibility state: updating should not force hidden geometries to show.
        is_visible = self._visible.get(name, True)
        self._geometries[name] = geometry
        self._materials[name] = self._make_material(geometry)
        self._visible[name] = is_visible
        if self.widget.scene.has_geometry(name):
            self.widget.scene.remove_geometry(name)
        if is_visible:
            self._add_to_scene(name)


    def remove_geometry(self, name: str = None):
        if name is None:
            name = self._geometry_name
        if self.widget.scene.has_geometry(name):
            self.widget.scene.remove_geometry(name)
        self._geometries.pop(name, None)
        self._materials.pop(name, None)
        self._visible.pop(name, None)

    def has_geometry(self, name: str) -> bool:
        return name in self._geometries

    def is_geometry_visible(self, name: str) -> bool:
        return self._visible.get(name, False)

    def set_geometry_visible(self, name: str, visible: bool):
        if name not in self._geometries:
            return
        prev = self._visible.get(name, False)
        self._visible[name] = bool(visible)
        if prev and not visible:
            if self.widget.scene.has_geometry(name):
                self.widget.scene.remove_geometry(name)
        elif (not prev) and visible:
            # Only add if not already present (idempotent).
            if not self.widget.scene.has_geometry(name):
                self._add_to_scene(name)


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


    def capture_image(self, on_image):
        self.widget.scene.scene.render_to_image(on_image)


    def get_view_state(self):
        camera = self.widget.scene.camera
        model_matrix = np.asarray(camera.get_model_matrix())
        width = self.widget.frame.width
        height = self.widget.frame.height
        
        return {
            'model_matrix': model_matrix.tolist(),
            'width': width,
            'height': height
        }
        
        
    def apply_view_state(self, params):
        model_matrix = np.array(params['model_matrix'])
        width = params['width']
        height = params['height']
        
        extrinsic = to_o3d_extrinsic_from_c2w(model_matrix)
        intrinsic = create_camera_intrinsic_from_size(width, height)
        
        bbox = o3d.geometry.AxisAlignedBoundingBox(
            self._bbox_origin.tolist(),
            (self._bbox_origin + self._bbox_size).tolist()
        )
        
        self.widget.setup_camera(intrinsic, extrinsic, width, height, bbox)
