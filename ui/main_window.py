import os
import glob
import numpy as np
from datetime import datetime
import open3d as o3d
import open3d.visualization.gui as gui

from ui.scene_view import SceneWidget
from ui.panels import SettingsPanel
from ui.camera_controller import CameraController
from tools.camera_view_io import save_view_state, load_view_state
from tools.screenshot import save_image
from tools.ply_io import load_ply_geometry


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
        self.camera = CameraController(
            window=self.window,
            scene_view=self.scene_view,
            settings_panel=self.settings_panel,
            register_geometry_toggle=self._register_geometry_toggle,
        )
        
        self._setup_callbacks()


    def init(self):
        self.scene_view.init()
        self.window.add_child(self.scene_view.widget)
        self.window.add_child(self.settings_panel.widget)
        self._update_ui_from_state()
        self._apply_scene_ui_settings()
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

        # Axis is fixed-size for simplicity (no UI for axis scale).
        axis = create_coordinate_frame(size=1.0)
        self.scene_view.update_geometry(axis, name="axis")
        # Start with axis hidden (checkbox unchecked by default).
        self.scene_view.set_geometry_visible("axis", False)
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
        self.settings_panel.black_background_checkbox.set_on_checked(self.on_black_background_checked)
        self.settings_panel.import_ply_button.set_on_clicked(self.on_import_ply_clicked)
        self.settings_panel.generate_button.set_on_clicked(self.on_generate_clicked)
        self.settings_panel.point_count_slider.set_on_value_changed(self.on_point_count_changed)
        self.settings_panel.size_slider.set_on_value_changed(self.on_size_changed)
        self.settings_panel.load_view_button.set_on_clicked(self.on_load_view)
        self.settings_panel.load_capture_button.set_on_clicked(self.on_load_capture)
        self.settings_panel.camera_scale_slider.set_on_value_changed(self.camera.on_camera_scale_changed)
        self.settings_panel.update_cameras_button.set_on_clicked(self.camera.on_update_cameras_clicked)
        self.settings_panel.add_camera_from_scene_button.set_on_clicked(self.camera.on_add_camera_from_scene_clicked)
        self.settings_panel.rerender_camera_images_button.set_on_clicked(self.camera.on_rerender_camera_images_clicked)
        self.settings_panel.delete_selected_camera_button.set_on_clicked(self.camera.on_delete_selected_camera_clicked)
        self.settings_panel.set_on_delete_camera_requested(self.camera.on_delete_camera_requested)
        self.settings_panel.show_all_cameras_button.set_on_clicked(self.camera.on_show_all_cameras_clicked)
        self.settings_panel.hide_all_cameras_button.set_on_clicked(self.camera.on_hide_all_cameras_clicked)
        self.settings_panel.export_camera_set_button.set_on_clicked(self.camera.on_export_camera_set_clicked)
        self.settings_panel.import_camera_set_button.set_on_clicked(self.camera.on_import_camera_set_clicked)


    def _update_ui_from_state(self):
        # Sliders show values directly; no extra labels to sync.
        pass

    def _apply_scene_ui_settings(self):
        # Default to black background, controlled by the checkbox.
        self.on_black_background_checked(self.settings_panel.black_background_checkbox.checked)

    def on_black_background_checked(self, is_checked: bool):
        if is_checked:
            self.scene_view.set_background_color([0.0, 0.0, 0.0, 1.0])
        else:
            # Light gray fallback (keeps UI readable without assuming Open3D's default).
            self.scene_view.set_background_color([0.95, 0.95, 0.95, 1.0])


    def on_generate_clicked(self):
        # Generate / update the point cloud only.
        points, colors = generate_point_cloud_data(
            count=self.point_count,
            size=self.geometry_size,
        )
        geometry = create_point_cloud(points, colors)
        self.scene_view.update_geometry(geometry, name="main_geometry")
        self._register_geometry_toggle("main_geometry", "Point Cloud")

    def on_import_ply_clicked(self):
        original_cwd = os.getcwd()
        start_dir = os.path.abspath(os.path.join("samples")) if os.path.exists("samples") else os.getcwd()

        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Import PLY", self.window.theme)
        dlg.add_filter(".ply", "PLY files")
        dlg.set_path(start_dir)

        def on_done(path):
            os.chdir(original_cwd)
            self.window.close_dialog()
            if not path or not os.path.exists(path):
                return

            geom = load_ply_geometry(path)
            print(f"Loaded PLY geometry: {geom}")
            if geom is None:
                return

            # Keep a single "ply" geometry that gets replaced on re-import.
            self.scene_view.update_geometry(geom, name="ply")
            self._register_geometry_toggle("ply", "PLY")
            self.scene_view.fit_camera_to_geometry(geom)

        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()

        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)


    def on_point_count_changed(self, value):
        self.point_count = self.settings_panel.point_count_slider.int_value


    def on_size_changed(self, value: float):
        self.geometry_size = self.settings_panel.size_slider.double_value


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
                self.camera.set_selected_view_path(path)
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
                self.camera.set_selected_image_path(path)
                self.settings_panel.set_selected_capture_file(path)
        
        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()
        
        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)
