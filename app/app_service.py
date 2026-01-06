from typing import Callable
from .app_state import AppState
from domain.example_logic import generate_point_cloud_data
from viz.geometry_factory import create_point_cloud, create_coordinate_frame
from infra.image_io import save_image

class AppService:
    def __init__(self):
        self.state = AppState()
        self._geometry_update_callbacks: list[Callable] = []
        self._state_change_callbacks: list[Callable] = []
    

    def register_geometry_update_callback(self, callback: Callable):
        self._geometry_update_callbacks.append(callback)
    

    def register_state_change_callback(self, callback: Callable):
        self._state_change_callbacks.append(callback)
    

    def _notify_geometry_update(self, geometry):
        for callback in self._geometry_update_callbacks:
            callback(geometry)
    

    def _notify_state_change(self):
        for callback in self._state_change_callbacks:
            callback(self.state)
    

    def generate_geometry(self):
        if self.state.geometry_type == "point_cloud":
            points, colors = generate_point_cloud_data(
                count=self.state.point_count,
                size=self.state.geometry_size
            )
            geometry = create_point_cloud(points, colors)
        else:
            geometry = create_coordinate_frame(size=self.state.geometry_size)
        
        self._notify_geometry_update(geometry)
    

    def update_point_count(self, count: int):
        self.state.point_count = count
        self._notify_state_change()
    

    def update_geometry_size(self, size: float):
        self.state.geometry_size = size
        self._notify_state_change()
    

    def update_geometry_type(self, geom_type: str):
        self.state.geometry_type = geom_type
        self._notify_state_change()


    def save_screenshot(self, scene_view, path):
        def on_image(image):
            save_image(path, image)

        scene_view.capture_image(on_image)