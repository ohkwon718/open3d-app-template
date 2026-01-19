import os
import glob
import numpy as np
from datetime import datetime
import open3d as o3d
import open3d.visualization.gui as gui

from ui.scene_view import SceneWidget
from ui.panels import SettingsPanel
from tools.view_io import save_view_state, load_view_state
from tools.screenshot import save_image
from tools.camera_viz import create_camera_geometry, create_o3d_intrinsic
from tools.camera_math import to_o3d_extrinsic_from_c2w, create_camera_intrinsic_from_size


def generate_point_cloud_data(count: int = 1000, size: float = 1.0):
    """Generate example point cloud data for demo purposes."""
    points = np.random.uniform(-size/2, size/2, (count, 3))
    colors = (points - points.min(axis=0)) / (points.max(axis=0) - points.min(axis=0) + 1e-8)
    colors = np.clip(colors, 0, 1)
    return points, colors


def create_point_cloud(points: np.ndarray, colors: np.ndarray) -> o3d.geometry.PointCloud:
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    pcd.colors = o3d.utility.Vector3dVector(colors)
    return pcd


def create_coordinate_frame(size: float = 1.0) -> o3d.geometry.TriangleMesh:
    return o3d.geometry.TriangleMesh.create_coordinate_frame(size=size)


class MainWindow:
    def __init__(self, title="Open3D App Template", window_size=(1680, 1050)):
        self.app = gui.Application.instance
        self.window = self.app.create_window(title, window_size[0], window_size[1])
        self.window.set_on_layout(self.on_layout)
        
        self.scene_view = SceneWidget(self.window)
        self.settings_panel = SettingsPanel(self.window)
        
        # State
        self.point_count = 10000
        self.geometry_size = 1.0
        self.camera_scale = 1.0
        self.geometry_type = "point_cloud"
        self.selected_view_path = None
        self.selected_image_path = None
        
        self._setup_callbacks()


    def init(self):
        self.scene_view.init()
        self.window.add_child(self.scene_view.widget)
        self.window.add_child(self.settings_panel.widget)
        self._update_ui_from_state()
        self._init_default_geometries()

    def _register_geometry_toggle(self, name: str, label: str):
        checked = self.scene_view.is_geometry_visible(name) if self.scene_view.has_geometry(name) else False

        def on_checked(is_checked: bool):
            self.scene_view.set_geometry_visible(name, is_checked)

        self.settings_panel.upsert_geometry_toggle(
            name=name,
            label=label,
            checked=checked,
            on_checked=on_checked,
        )


    def _init_default_geometries(self):
        # Initialize both geometries on startup:
        # - main point cloud (10k points by default)
        # - coordinate axes at origin
        points, colors = generate_point_cloud_data(
            count=self.point_count,
            size=self.geometry_size,
        )
        pcd = create_point_cloud(points, colors)
        self.scene_view.update_geometry(pcd, name="main_geometry")
        self._register_geometry_toggle("main_geometry", "Point Cloud")

        axis = create_coordinate_frame(size=self.geometry_size)
        self.scene_view.update_geometry(axis, name="axis")
        self._register_geometry_toggle("axis", "Axis")
        self.scene_view.fit_camera_to_geometry(pcd)


    def on_layout(self, layout_context):
        r = self.window.content_rect
        em = self.window.theme.font_size
        width_panel = 18 * em
        
        self.scene_view.widget.frame = gui.Rect(
            r.x, r.y, r.width - width_panel, r.height
        )
        self.settings_panel.widget.frame = gui.Rect(
            r.x + r.width - width_panel, r.y, width_panel, r.height
        )


    def _setup_callbacks(self):
        self.settings_panel.screenshot_button.set_on_clicked(self.on_save_screenshot)
        self.settings_panel.save_camera_button.set_on_clicked(self.on_save_camera)
        self.settings_panel.load_camera_button.set_on_clicked(self.on_load_camera)
        self.settings_panel.load_latest_camera_button.set_on_clicked(self.on_load_latest_camera)
        self.settings_panel.generate_button.set_on_clicked(self.on_generate_clicked)
        self.settings_panel.point_count_slider.set_on_value_changed(self.on_point_count_changed)
        self.settings_panel.size_slider.set_on_value_changed(self.on_size_changed)
        self.settings_panel.load_view_button.set_on_clicked(self.on_load_view)
        self.settings_panel.load_capture_button.set_on_clicked(self.on_load_capture)
        self.settings_panel.camera_scale_slider.set_on_value_changed(self.on_camera_scale_changed)
        self.settings_panel.update_cameras_button.set_on_clicked(self.on_update_cameras_clicked)


    def _update_ui_from_state(self):
        self.settings_panel.set_point_count_label(self.point_count)
        self.settings_panel.set_size_label(self.geometry_size)
        self.settings_panel.set_camera_scale_label(self.camera_scale)


    def on_generate_clicked(self):
        # Geometry type is selected via tabs in the panel.
        self.geometry_type = self.settings_panel.get_generation_geometry_type()
        if self.geometry_type == "point_cloud":
            points, colors = generate_point_cloud_data(
                count=self.point_count,
                size=self.geometry_size
            )
            geometry = create_point_cloud(points, colors)
            self.scene_view.update_geometry(geometry, name="main_geometry")
            self._register_geometry_toggle("main_geometry", "Point Cloud")
            # Keep axis visible; only update its scale when size changes.
            axis = create_coordinate_frame(size=self.geometry_size)
            self.scene_view.update_geometry(axis, name="axis")
            self._register_geometry_toggle("axis", "Axis")
        elif self.geometry_type == "coordinate_frame":
            geometry = create_coordinate_frame(size=self.geometry_size)
            self.scene_view.update_geometry(geometry, name="axis")
            self._register_geometry_toggle("axis", "Axis")


    def on_point_count_changed(self, value):
        self.point_count = self.settings_panel.point_count_slider.int_value
        self.settings_panel.set_point_count_label(self.point_count)


    def on_size_changed(self, value: float):
        self.geometry_size = self.settings_panel.size_slider.double_value
        self.settings_panel.set_size_label(self.geometry_size)

    def on_camera_scale_changed(self, value: float):
        self.camera_scale = self.settings_panel.camera_scale_slider.double_value
        self.settings_panel.set_camera_scale_label(self.camera_scale)

    def on_update_cameras_clicked(self):
        # Use selected view and image files
        if not (self.selected_view_path and os.path.exists(self.selected_view_path)):
            return

        params = load_view_state(self.selected_view_path)
        model_matrix = np.array(params["model_matrix"])
        width = params["width"]
        height = params["height"]

        extrinsic = to_o3d_extrinsic_from_c2w(model_matrix)
        intrinsic = create_o3d_intrinsic(size=(width, height))

        img_array = None
        if self.selected_image_path and os.path.exists(self.selected_image_path):
            img_o3d = o3d.io.read_image(self.selected_image_path)
            img_array = np.asarray(img_o3d)

        geometries = create_camera_geometry(
            intrinsic=intrinsic,
            extrinsic=extrinsic,
            img=img_array,
            scale=self.camera_scale,
            O3DVisualizer=True,
        )

        # Update (not remove/add) so hidden state stays hidden if user unchecked it.
        if len(geometries) > 0:
            self.scene_view.update_geometry(geometries[0], name="camera_frustum")
            self._register_geometry_toggle("camera_frustum", "Camera Frustum")
        if len(geometries) > 1:
            self.scene_view.update_geometry(geometries[1], name="camera_image")
            self._register_geometry_toggle("camera_image", "Camera Image")


    def on_geometry_type_changed(self, text: str, index: int):
        if index == 0:
            self.geometry_type = "point_cloud"
        elif index == 1:
            self.geometry_type = "coordinate_frame"
        else:
            self.geometry_type = "cameras"


    def on_save_screenshot(self):
        path = self._make_screenshot_path()
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        
        def on_image(image):
            save_image(abs_path, image)
        
        self.scene_view.capture_image(on_image)


    def on_save_camera(self):
        path = self._make_camera_path()
        abs_path = os.path.abspath(path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        params = self.scene_view.get_view_state()
        save_view_state(abs_path, params)


    def on_load_camera(self):
        original_cwd = os.getcwd()
        views_dir = os.path.join("export", "views")
        
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Load Camera View", 
                            self.window.theme)
        dlg.add_filter(".json", "JSON files")
        if os.path.exists(views_dir):
            abs_path = os.path.abspath(views_dir)
            dlg.set_path(abs_path)
        
        def on_done(path):
            os.chdir(original_cwd)
            self.window.close_dialog()
            if path:
                params = load_view_state(path)
                self.scene_view.apply_view_state(params)
        
        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()
        
        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)


    def on_load_latest_camera(self):
        views_dir = os.path.abspath(os.path.join("export", "views"))
        pattern = os.path.join(views_dir, "camera_view_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return
        latest_file = max(files, key=os.path.getmtime)
        params = load_view_state(latest_file)
        self.scene_view.apply_view_state(params)


    def _make_screenshot_path(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join("export", "screenshots", f"screenshot_{ts}.png")


    def _make_camera_path(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join("export", "views", f"camera_view_{ts}.json")


    def on_load_view(self):
        original_cwd = os.getcwd()
        views_dir = os.path.join("export", "views")
        
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Load View", 
                            self.window.theme)
        dlg.add_filter(".json", "JSON files")
        if os.path.exists(views_dir):
            abs_path = os.path.abspath(views_dir)
            dlg.set_path(abs_path)
        
        def on_done(path):
            os.chdir(original_cwd)
            self.window.close_dialog()
            if path:
                self.selected_view_path = path
                self.settings_panel.set_selected_view_file(path)
        
        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()
        
        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)


    def on_load_capture(self):
        original_cwd = os.getcwd()
        screenshots_dir = os.path.join("export", "screenshots")
        
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Load Image", 
                            self.window.theme)
        dlg.add_filter(".png", "PNG files")
        dlg.add_filter(".jpg", "JPG files")
        dlg.add_filter(".jpeg", "JPEG files")
        if os.path.exists(screenshots_dir):
            abs_path = os.path.abspath(screenshots_dir)
            dlg.set_path(abs_path)
        
        def on_done(path):
            os.chdir(original_cwd)
            self.window.close_dialog()
            if path:
                self.selected_image_path = path
                self.settings_panel.set_selected_capture_file(path)
        
        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()
        
        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)
