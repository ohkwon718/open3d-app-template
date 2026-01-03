import open3d.visualization.gui as gui


class SettingsPanel:
    def __init__(self):
        self.widget = gui.Vert(0, gui.Margins(0.5, 0.5, 0.5, 0.5))
        
        self.widget.add_child(gui.Label("Settings"))
        self.widget.add_fixed(10)
        
        self.generate_button = gui.Button("Generate / Update Geometry")
        self.widget.add_child(self.generate_button)
        self.widget.add_fixed(10)
        
        self.widget.add_child(gui.Label("Point Count"))
        self.point_count_slider = gui.Slider(gui.Slider.INT)
        self.point_count_slider.set_limits(100, 10000)
        self.point_count_slider.int_value = 1000
        self.widget.add_child(self.point_count_slider)
        self.point_count_label = gui.Label("1000")
        self.widget.add_child(self.point_count_label)
        self.widget.add_fixed(10)
        
        self.widget.add_child(gui.Label("Geometry Size"))
        self.size_slider = gui.Slider(gui.Slider.DOUBLE)
        self.size_slider.set_limits(0.1, 5.0)
        self.size_slider.double_value = 1.0
        self.widget.add_child(self.size_slider)
        self.size_label = gui.Label("1.0")
        self.widget.add_child(self.size_label)
        self.widget.add_fixed(10)
        
        self.widget.add_child(gui.Label("Geometry Type"))
        self.geom_type_combo = gui.Combobox()
        self.geom_type_combo.add_item("Point Cloud")
        self.geom_type_combo.add_item("Coordinate Frame")
        self.geom_type_combo.selected_index = 0
        self.widget.add_child(self.geom_type_combo)
    

    def set_point_count_label(self, value: int):
        self.point_count_label.text = str(value)
    

    def set_size_label(self, value: float):
        self.size_label.text = f"{value:.2f}"
