import open3d.visualization.gui as gui

class SettingsPanel:
    def __init__(self):
        self.widget = gui.Vert(0, gui.Margins(0.5, 0.5, 0.5, 0.5))
        
        # Add some dummy content
        self.widget.add_child(gui.Label("Settings Panel"))
        self.widget.add_fixed(10)
        self.widget.add_child(gui.Label("Dummy controls will go here"))
        self.widget.add_fixed(10)
        self.widget.add_child(gui.Label("Panel on the right side"))

    def __call__(self):
        return self.widget