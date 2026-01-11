import os
import glob
from datetime import datetime
import open3d.visualization.gui as gui

from ui.scene_view import SceneView
from ui.panels import SettingsPanel
from app.app_service import AppService


class InteractionController:
    def __init__(self, window, scene_view: SceneView, settings_panel: SettingsPanel, 
                 app_service: AppService):
        self.window = window
        self.scene_view = scene_view
        self.settings_panel = settings_panel
        self.app_service = app_service
    

    def setup_callbacks(self):
        self.app_service.register_geometry_update_callback(self.on_geometry_updated)
        self.app_service.register_state_change_callback(self.on_state_changed)
        
        self.settings_panel.screenshot_button.set_on_clicked(
            self.on_save_screenshot
        )
        self.settings_panel.save_camera_button.set_on_clicked(
            self.on_save_camera
        )
        self.settings_panel.load_camera_button.set_on_clicked(
            self.on_load_camera
        )
        self.settings_panel.load_latest_camera_button.set_on_clicked(
            self.on_load_latest_camera
        )
        self.settings_panel.generate_button.set_on_clicked(
            self.on_generate_clicked
        )
        self.settings_panel.point_count_slider.set_on_value_changed(
            self.on_point_count_changed
        )
        self.settings_panel.size_slider.set_on_value_changed(
            self.on_size_changed
        )
        self.settings_panel.geom_type_combo.set_on_selection_changed(
            self.on_geometry_type_changed
        )
        self.on_state_changed(self.app_service.state)
    

    def on_generate_clicked(self):
        self.app_service.generate_geometry()
    

    def on_point_count_changed(self, value):
        int_value = self.settings_panel.point_count_slider.int_value
        self.app_service.update_point_count(int_value)
    

    def on_size_changed(self, value: float):
        self.app_service.update_geometry_size(value)
    

    def on_geometry_type_changed(self, index: int, text: str):
        geom_type = "point_cloud" if index == 0 else "coordinate_frame"
        self.app_service.update_geometry_type(geom_type)
    

    def on_geometry_updated(self, geometry):
        self.scene_view.update_geometry(geometry)
    

    def on_state_changed(self, state):
        self.settings_panel.set_point_count_label(state.point_count)
        self.settings_panel.set_size_label(state.geometry_size)


    def on_save_screenshot(self):
        path = self._make_screenshot_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.app_service.save_screenshot(self.scene_view, path)


    def on_save_camera(self):
        path = self._make_camera_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.app_service.save_view_state(self.scene_view, path)


    def on_load_camera(self):
        views_dir = os.path.join("export", "views")
        
        dlg = gui.FileDialog(gui.FileDialog.OPEN, "Load Camera View", 
                            self.window.theme)
        dlg.add_filter(".json", "JSON files")
        if os.path.exists(views_dir):
            dlg.set_path(views_dir)
        
        def on_done(path):
            self.window.close_dialog()
            if path:
                self.app_service.load_view_state(self.scene_view, path)
        
        def on_cancel():
            self.window.close_dialog()
        
        dlg.set_on_cancel(on_cancel)
        dlg.set_on_done(on_done)
        self.window.show_dialog(dlg)


    def on_load_latest_camera(self):
        views_dir = os.path.join("export", "views")
        pattern = os.path.join(views_dir, "camera_view_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return
        latest_file = max(files, key=os.path.getmtime)
        self.app_service.load_view_state(self.scene_view, latest_file)
    

    def _make_screenshot_path(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join("export", "screenshots", f"screenshot_{ts}.png")
    
    
    def _make_camera_path(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return os.path.join("export", "views", f"camera_view_{ts}.json")