import open3d.visualization.gui as gui
from .scene_view import SceneView
from .panels import SettingsPanel


class MainWindow:
    def __init__(self, title="Open3D App Template", window_size=(1680, 1050)):
        self.app = gui.Application.instance
        self.window = self.app.create_window(title, window_size[0], window_size[1])
        self.window.set_on_layout(self.on_layout)
        
        self.scene_view = SceneView(self.window)
        self.settings_panel = SettingsPanel()
    

    def init(self):
        self.scene_view.init()
        self.window.add_child(self.scene_view.widget)
        self.window.add_child(self.settings_panel.widget)
    

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
