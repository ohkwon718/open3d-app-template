import os
import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui

from tools.camera_viz import create_camera_geometry, create_o3d_intrinsic
from tools.camera_math import to_o3d_extrinsic_from_c2w
from tools.camera_set_io import export_camera_set, load_camera_set, load_camera_image_array, make_camera_record
from tools.camera_view_io import load_view_state


class CameraController:
    """
    Groups camera-related state + UI handlers to keep MainWindow small.
    This is not a framework layer—just a convenience wrapper around existing Open3D calls.
    """

    def __init__(self, *, window, scene_view, settings_panel, register_geometry_toggle):
        self.window = window
        self.scene_view = scene_view
        self.settings_panel = settings_panel
        self._register_geometry_toggle = register_geometry_toggle

        self.camera_scale = 1.0
        self._camera_instance_counter = 0
        self._camera_records: dict[int, dict] = {}

        self.selected_view_path: str | None = None
        self.selected_image_path: str | None = None

    # --- wiring helpers ---
    def set_selected_view_path(self, path: str | None):
        self.selected_view_path = path

    def set_selected_image_path(self, path: str | None):
        self.selected_image_path = path

    # --- callbacks ---
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
        # Add from files (view required, capture optional)
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

        if len(geometries) > 0:
            self.scene_view.update_geometry(geometries[0], name=frustum_name)
            self._register_geometry_toggle(frustum_name, f"Camera {idx} Frustum")
        if len(geometries) > 1:
            self.scene_view.update_geometry(geometries[1], name=image_name)
            self._register_geometry_toggle(image_name, f"Camera {idx} Image")

    def on_add_camera_from_scene_clicked(self):
        params = self.scene_view.get_view_state()
        model_matrix = np.array(params["model_matrix"])
        width = params["width"]
        height = params["height"]

        extrinsic = to_o3d_extrinsic_from_c2w(model_matrix)
        intrinsic = create_o3d_intrinsic(size=(width, height))

        def on_image(image):
            img_array = np.asarray(image)
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

    def on_rerender_camera_images_clicked(self):
        indices = self.settings_panel.list_camera_indices()
        if not indices:
            return

        original_view = self.scene_view.get_view_state()

        capture_w = int(original_view.get("width", 0))
        capture_h = int(original_view.get("height", 0))
        if capture_w <= 0 or capture_h <= 0:
            return

        # Prevent self-feedback: if we capture the scene *including* the existing
        # textured camera image planes, each rerender "bakes in" the previous image,
        # making the result progressively darker. Hide image planes during capture.
        camera_image_visibility: dict[str, bool] = {}
        for name in self.settings_panel.list_visibility_names():
            if name.startswith("camera_image_") and self.scene_view.has_geometry(name):
                camera_image_visibility[name] = self.scene_view.is_geometry_visible(name)
                self.scene_view.set_geometry_visible(name, False)

        idx_list = list(indices)
        pos = {"i": 0}
        app = gui.Application.instance

        def render_next():
            if pos["i"] >= len(idx_list):
                self.scene_view.apply_view_state(original_view)
                for name, was_visible in camera_image_visibility.items():
                    self.scene_view.set_geometry_visible(name, was_visible)
                return

            idx = idx_list[pos["i"]]
            pos["i"] += 1

            rec = self._camera_records.get(idx)
            if rec is None:
                render_next()
                return

            model_matrix = rec.get("model_matrix")
            extrinsic_list = rec.get("extrinsic")
            intrinsic_dict = rec.get("intrinsic") or {}
            fx = intrinsic_dict.get("fx")
            fy = intrinsic_dict.get("fy")
            cx = intrinsic_dict.get("cx")
            cy = intrinsic_dict.get("cy")

            if model_matrix is None or extrinsic_list is None or fx is None or fy is None or cx is None or cy is None:
                render_next()
                return

            params = {
                "model_matrix": model_matrix,
                "width": capture_w,
                "height": capture_h,
            }
            self.scene_view.apply_view_state(params)
            self.window.post_redraw()

            def on_image(image):
                img_array = np.asarray(image)
                if img_array.size == 0:
                    render_next()
                    return

                rec["image_array"] = img_array
                rec["image_path"] = None

                intrinsic = o3d.camera.PinholeCameraIntrinsic(
                    capture_w, capture_h, float(fx), float(fy), float(cx), float(cy)
                )
                extrinsic = np.array(extrinsic_list, dtype=np.float64)

                geometries = create_camera_geometry(
                    intrinsic=intrinsic,
                    extrinsic=extrinsic,
                    img=img_array,
                    scale=self.camera_scale,
                    O3DVisualizer=False,
                )

                frustum_name = f"camera_frustum_{idx}"
                image_name = f"camera_image_{idx}"
                if len(geometries) > 0:
                    self.scene_view.update_geometry(geometries[0], name=frustum_name)
                    self._register_geometry_toggle(frustum_name, f"Camera {idx} Frustum")
                if len(geometries) > 1:
                    self.scene_view.update_geometry(geometries[1], name=image_name)
                    self._register_geometry_toggle(image_name, f"Camera {idx} Image")

                render_next()

            app.post_to_main_thread(self.window, lambda: self.scene_view.capture_image(on_image))

        render_next()

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

    def on_export_camera_set_clicked(self):
        indices = self.settings_panel.list_camera_indices()
        if not indices:
            return
        export_camera_set(indices=indices, camera_records=self._camera_records)

    def on_import_camera_set_clicked(self):
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

                model_matrix = np.array(cam.get("model_matrix") or cam.get("c2w"), dtype=np.float64)
                extrinsic_list = cam.get("extrinsic")
                extrinsic = np.array(extrinsic_list, dtype=np.float64) if extrinsic_list is not None else to_o3d_extrinsic_from_c2w(model_matrix)

                intrinsic_dict = cam.get("intrinsic") or {}
                fx = intrinsic_dict.get("fx")
                fy = intrinsic_dict.get("fy")
                cx = intrinsic_dict.get("cx")
                cy = intrinsic_dict.get("cy")
                if fx is None or fy is None or cx is None or cy is None:
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

