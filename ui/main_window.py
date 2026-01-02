import numpy as np
import open3d.visualization.gui as gui
import open3d as o3d
import open3d.visualization.rendering as rendering
from .scene_view import SceneView
from .panels import SettingsPanel

class MainWindow:
    def __init__(self, title="Open3D", window_size=(1680, 1050), bbox_origin=np.array([0, 0, 0]), bbox_size=np.array([1, 1, 1])):
        self.app = gui.Application.instance
        self.app.initialize()

        self.window  = gui.Application.instance.create_window(title, window_size[0], window_size[1])
        self.window.set_on_layout(self.on_layout)            

        self.scene_view = SceneView(self.window)
        self.panels = SettingsPanel()


    def init(self):
        self.scene_view.init()
        self.window.add_child(self.scene_view.widget)
        self.window.add_child(self.panels.widget)


    def run(self):
        self.app.run()


    def add_geometry(self, geometry):
        self.window.add_geometry(geometry)

    
    def on_layout(self, layout_context):
        r = self.window.content_rect
        em = self.window.theme.font_size
        width_panel = 18 * em
        
        # Scene view on the left
        self.scene_view.widget.frame = gui.Rect(
            r.x, r.y, r.width - width_panel, r.height
        )
        # Settings panel on the right
        self.panels.widget.frame = gui.Rect(
            r.x + r.width - width_panel, r.y, width_panel, r.height
        ) 

    def __call__(self):
        return self.window

    def __del__(self):
        self.window.close()
