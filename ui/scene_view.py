import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

class SceneView:
    def __init__(self, window):
        self.window = window        
        
    def init(self):
        w = self.window
        self.widget = gui.SceneWidget()
        self.widget.scene = rendering.Open3DScene(w.renderer)        
        self.widget.scene.show_skybox(False)
        self.widget.scene.set_lighting(self.widget.scene.LightingProfile.NO_SHADOWS, (0, 0, 0))

        self.origin = np.array([0, 0, 0])
        self.bb_size = np.array([1, 1, 1])
        self.bbox = o3d.geometry.AxisAlignedBoundingBox(self.origin.tolist(), (self.origin+self.bb_size).tolist())        
        self.bbox.color = (0.0, 0.0, 0.0)
        self.widget.setup_camera(60, self.bbox, [0, 0, 0])


    def on_layout(self, window):
        pass

    def __call__(self):
        return self.widget