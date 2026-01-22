import os
import glob
import numpy as np
from datetime import datetime
import open3d as o3d
import open3d.visualization.gui as gui

from ui.scene_view import SceneWidget
from ui.panels import SettingsPanel
from tools.camera_view_io import save_view_state, load_view_state
from tools.screenshot import save_image
from tools.camera_viz import create_camera_geometry, create_o3d_intrinsic
from tools.camera_math import to_o3d_extrinsic_from_c2w, create_camera_intrinsic_from_size
from tools.camera_set_io import (
    export_camera_set,
    load_camera_set,
    load_camera_image_array,
    make_camera_record,
)


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
        self._camera_instance_counter = 0
        self._camera_records: dict[int, dict] = {}
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
        self.settings_panel.generate_button.set_on_clicked(self.on_generate_clicked)
        self.settings_panel.point_count_slider.set_on_value_changed(self.on_point_count_changed)
        self.settings_panel.size_slider.set_on_value_changed(self.on_size_changed)
        self.settings_panel.load_view_button.set_on_clicked(self.on_load_view)
        self.settings_panel.load_capture_button.set_on_clicked(self.on_load_capture)
        self.settings_panel.camera_scale_slider.set_on_value_changed(self.on_camera_scale_changed)
        self.settings_panel.update_cameras_button.set_on_clicked(self.on_update_cameras_clicked)
        self.settings_panel.add_camera_from_scene_button.set_on_clicked(self.on_add_camera_from_scene_clicked)
        self.settings_panel.delete_selected_camera_button.set_on_clicked(self.on_delete_selected_camera_clicked)
        self.settings_panel.set_on_delete_camera_requested(self.on_delete_camera_requested)
        self.settings_panel.show_all_cameras_button.set_on_clicked(self.on_show_all_cameras_clicked)
        self.settings_panel.hide_all_cameras_button.set_on_clicked(self.on_hide_all_cameras_clicked)
        self.settings_panel.export_camera_set_button.set_on_clicked(self.on_export_camera_set_clicked)
        self.settings_panel.import_camera_set_button.set_on_clicked(self.on_import_camera_set_clicked)


    def _update_ui_from_state(self):
        # Sliders show values directly; no extra labels to sync.
        pass


    def on_generate_clicked(self):
        # Generate / update the point cloud only.
        points, colors = generate_point_cloud_data(
            count=self.point_count,
            size=self.geometry_size,
        )
        geometry = create_point_cloud(points, colors)
        self.scene_view.update_geometry(geometry, name="main_geometry")
        self._register_geometry_toggle("main_geometry", "Point Cloud")


    def on_point_count_changed(self, value):
        self.point_count = self.settings_panel.point_count_slider.int_value


    def on_size_changed(self, value: float):
        self.geometry_size = self.settings_panel.size_slider.double_value

    def on_camera_scale_changed(self, value: float):
        self.camera_scale = self.settings_panel.camera_scale_slider.double_value

    def _is_camera_geometry_name(self, name: str) -> bool:
        return name.startswith("camera_frustum_") or name.startswith("camera_image_")

    def _set_all_cameras_visible(self, visible: bool):
        for name in self.settings_panel.list_visibility_names():
            if not self._is_camera_geometry_name(name):
                continue
            self.scene_view.set_geometry_visible(name, visible)

    def on_show_all_cameras_clicked(self):
        self._set_all_cameras_visible(True)

    def on_hide_all_cameras_clicked(self):
        self._set_all_cameras_visible(False)

    def on_update_cameras_clicked(self):
        # Add a new camera visualization (each click appends a new numbered camera).
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
            O3DVisualizer=False,
        )

        self._camera_instance_counter += 1
        idx = self._camera_instance_counter
        frustum_name = f"camera_frustum_{idx}"
        image_name = f"camera_image_{idx}"
        self.settings_panel.upsert_camera_item(idx)
        self._camera_records[idx] = make_camera_record(
            source="files",
            width=width,
            height=height,
            model_matrix=model_matrix,
            extrinsic=extrinsic,
            intrinsic=intrinsic,
            image_path=self.selected_image_path if (self.selected_image_path and os.path.exists(self.selected_image_path)) else None,
            image_array=None,
        )

        # Use update_geometry so re-clicking after hiding keeps hidden state hidden,
        # and the registry stays consistent.
        if len(geometries) > 0:
            self.scene_view.update_geometry(geometries[0], name=frustum_name)
            self._register_geometry_toggle(frustum_name, f"Camera {idx} Frustum")
        if len(geometries) > 1:
            self.scene_view.update_geometry(geometries[1], name=image_name)
            self._register_geometry_toggle(image_name, f"Camera {idx} Image")

    def on_add_camera_from_scene_clicked(self):
        """
        Adds a camera frustum from the *current* viewer camera (no files required).
        Uses SceneWidget.get_view_state() -> model_matrix/width/height.
        """
        params = self.scene_view.get_view_state()
        model_matrix = np.array(params["model_matrix"])
        width = params["width"]
        height = params["height"]

        extrinsic = to_o3d_extrinsic_from_c2w(model_matrix)
        intrinsic = create_o3d_intrinsic(size=(width, height))

        # Capture a screenshot and use it as the camera "image plane" texture.
        def on_image(image):
            img_array = np.asarray(image)

            # Default behavior: do NOT write screenshots to disk when adding from scene.
            # (User can still manually save via View -> Screenshot.)

            geometries = create_camera_geometry(
                intrinsic=intrinsic,
                extrinsic=extrinsic,
                img=img_array,
                scale=self.camera_scale,
                O3DVisualizer=False,
            )

            self._camera_instance_counter += 1
            idx = self._camera_instance_counter
            frustum_name = f"camera_frustum_{idx}"
            image_name = f"camera_image_{idx}"

            # Keep naming consistent regardless of source.
            self.settings_panel.upsert_camera_item(idx)
            self._camera_records[idx] = make_camera_record(
                source="scene",
                width=width,
                height=height,
                model_matrix=model_matrix,
                extrinsic=extrinsic,
                intrinsic=intrinsic,
                image_path=None,
                image_array=img_array,
            )

            if len(geometries) > 0:
                self.scene_view.update_geometry(geometries[0], name=frustum_name)
                self._register_geometry_toggle(frustum_name, f"Camera {idx} Frustum")
            if len(geometries) > 1:
                self.scene_view.update_geometry(geometries[1], name=image_name)
                self._register_geometry_toggle(image_name, f"Camera {idx} Image")

        self.scene_view.capture_image(on_image)

    def on_export_camera_set_clicked(self):
        """
        Prototype exporter:
        export/camera_sets/<timestamp>/
          cameras.json
          images/cam_###.png
        """
        indices = self.settings_panel.list_camera_indices()
        if not indices:
            return
        export_camera_set(indices=indices, camera_records=self._camera_records)

    def on_import_camera_set_clicked(self):
        """
        Import an exported camera set. For robustness, user selects the cameras.json file.
        Recreates camera frustums + optional image planes and appends them to the current list.
        """
        original_cwd = os.getcwd()
        sets_dir = os.path.abspath(os.path.join("export", "camera_sets"))

        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Import Camera Set (select cameras.json)", self.window.theme)
        dlg.add_filter(".json", "JSON files")
        if os.path.exists(sets_dir):
            dlg.set_path(sets_dir)

        def on_done(path):
            os.chdir(original_cwd)
            self.window.close_dialog()
            if not path or not os.path.exists(path):
                return
            try:
                payload, base_dir = load_camera_set(path)
            except Exception:
                return
            cameras = payload.get("cameras", [])
            if not isinstance(cameras, list):
                return

            for cam in cameras:
                try:
                    width = int(cam.get("width"))
                    height = int(cam.get("height"))
                except Exception:
                    continue

                # Prefer exported matrices; fall back to model_matrix (c2w) if needed.
                model_matrix = np.array(cam.get("model_matrix") or cam.get("c2w"), dtype=np.float64)
                extrinsic_list = cam.get("extrinsic")
                extrinsic = np.array(extrinsic_list, dtype=np.float64) if extrinsic_list is not None else to_o3d_extrinsic_from_c2w(model_matrix)

                intrinsic_dict = cam.get("intrinsic") or {}
                fx = intrinsic_dict.get("fx")
                fy = intrinsic_dict.get("fy")
                cx = intrinsic_dict.get("cx")
                cy = intrinsic_dict.get("cy")
                if fx is None or fy is None or cx is None or cy is None:
                    # Fallback to current helper if missing.
                    intrinsic = create_o3d_intrinsic(size=(width, height))
                else:
                    intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, float(fx), float(fy), float(cx), float(cy))

                img_array, image_path = load_camera_image_array(base_dir, cam.get("image_file"))

                geometries = create_camera_geometry(
                    intrinsic=intrinsic,
                    extrinsic=extrinsic,
                    img=img_array,
                    scale=self.camera_scale,
                    O3DVisualizer=False,
                )

                self._camera_instance_counter += 1
                idx = self._camera_instance_counter
                frustum_name = f"camera_frustum_{idx}"
                image_name = f"camera_image_{idx}"

                self.settings_panel.upsert_camera_item(idx)
                self._camera_records[idx] = make_camera_record(
                    source="import",
                    width=width,
                    height=height,
                    model_matrix=model_matrix,
                    extrinsic=extrinsic,
                    intrinsic=intrinsic,
                    image_path=image_path if (image_path and os.path.exists(image_path)) else None,
                    image_array=None,
                )

                if len(geometries) > 0:
                    self.scene_view.update_geometry(geometries[0], name=frustum_name)
                    self._register_geometry_toggle(frustum_name, f"Camera {idx} Frustum")
                if len(geometries) > 1:
                    self.scene_view.update_geometry(geometries[1], name=image_name)
                    self._register_geometry_toggle(image_name, f"Camera {idx} Image")

        def on_cancel():
            os.chdir(original_cwd)
            self.window.close_dialog()

        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)

    def _try_parse_camera_index(self, geometry_name: str) -> int | None:
        if geometry_name.startswith("camera_frustum_"):
            suffix = geometry_name.removeprefix("camera_frustum_")
        elif geometry_name.startswith("camera_image_"):
            suffix = geometry_name.removeprefix("camera_image_")
        else:
            return None
        try:
            return int(suffix)
        except ValueError:
            return None

    def _delete_camera_index(self, idx: int):
        frustum_name = f"camera_frustum_{idx}"
        image_name = f"camera_image_{idx}"

        if self.scene_view.has_geometry(frustum_name):
            self.scene_view.remove_geometry(frustum_name)
        self.settings_panel.remove_geometry_toggle(frustum_name)

        if self.scene_view.has_geometry(image_name):
            self.scene_view.remove_geometry(image_name)
        self.settings_panel.remove_geometry_toggle(image_name)

        self.settings_panel.remove_camera_item(idx)
        self._camera_records.pop(idx, None)

    def on_delete_selected_camera_clicked(self):
        idx = self.settings_panel.get_selected_camera_index()
        if idx is None:
            return
        self._delete_camera_index(idx)

    def on_delete_camera_requested(self, idx: int):
        self._delete_camera_index(idx)


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
