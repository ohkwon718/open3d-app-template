import open3d.visualization.gui as gui


class SettingsPanel:
    def __init__(self, window):
        em = window.theme.font_size
        separation_height = int(round(0.5 * em))
        self.widget = gui.Vert(0, gui.Margins(0.5 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        self.widget.add_fixed(separation_height)
        
        
        view_group = gui.CollapsableVert("View", 0.25 * em, gui.Margins(em, 0, 0, 0))
        screenshot_row = gui.Horiz(0.25 * em)
        screenshot_label = gui.Label('Screenshot')
        screenshot_row.add_child(screenshot_label)
        self.screenshot_button = gui.Button("Save")
        self.screenshot_button.horizontal_padding_em = 0.5
        self.screenshot_button.vertical_padding_em = 0
        screenshot_row.add_child(self.screenshot_button)
        view_group.add_child(screenshot_row)
        
        camera_label = gui.Label('Camera View')
        view_group.add_child(camera_label)
        
        camera_row = gui.Horiz(0.25 * em)
        self.save_camera_button = gui.Button("Save")
        self.save_camera_button.horizontal_padding_em = 0.5
        self.save_camera_button.vertical_padding_em = 0
        camera_row.add_child(self.save_camera_button)
        self.load_camera_button = gui.Button("Load")
        self.load_camera_button.horizontal_padding_em = 0.5
        self.load_camera_button.vertical_padding_em = 0
        camera_row.add_child(self.load_camera_button)
        self.load_latest_camera_button = gui.Button("Load Latest")
        self.load_latest_camera_button.horizontal_padding_em = 0.5
        self.load_latest_camera_button.vertical_padding_em = 0
        camera_row.add_child(self.load_latest_camera_button)
        view_group.add_child(camera_row)
        self.widget.add_child(view_group)
        self.widget.add_fixed(separation_height)
        

        self.widget.add_child(gui.Label("Settings"))
        self.widget.add_fixed(10)
        
        generation_group = gui.CollapsableVert("Generation", 0.25 * em, gui.Margins(em, 0, 0, 0))
        generate_row = gui.Horiz(0.25 * em)
        generate_label = gui.Label('Generate')
        generate_row.add_child(generate_label)
        self.generate_button = gui.Button("Generate / Update Geometry")
        generate_row.add_child(self.generate_button)
        generation_group.add_child(generate_row)
        self.widget.add_child(generation_group)
        self.widget.add_fixed(10)
        
        geometry_group = gui.CollapsableVert("Geometry Settings", 0.25 * em, gui.Margins(em, 0, 0, 0))
        point_count_row = gui.Horiz(0.25 * em)
        point_count_label = gui.Label("Point Count")
        point_count_row.add_child(point_count_label)
        self.point_count_slider = gui.Slider(gui.Slider.INT)
        self.point_count_slider.set_limits(100, 10000)
        self.point_count_slider.int_value = 1000
        point_count_row.add_child(self.point_count_slider)
        self.point_count_label = gui.Label("1000")
        point_count_row.add_child(self.point_count_label)
        geometry_group.add_child(point_count_row)
        geometry_group.add_fixed(10)
        
        size_row = gui.Horiz(0.25 * em)
        size_label = gui.Label("Geometry Size")
        size_row.add_child(size_label)
        self.size_slider = gui.Slider(gui.Slider.DOUBLE)
        self.size_slider.set_limits(0.1, 5.0)
        self.size_slider.double_value = 1.0
        size_row.add_child(self.size_slider)
        self.size_label = gui.Label("1.0")
        size_row.add_child(self.size_label)
        geometry_group.add_child(size_row)
        geometry_group.add_fixed(10)
        
        geom_type_row = gui.Horiz(0.25 * em)
        geom_type_label = gui.Label("Geometry Type")
        geom_type_row.add_child(geom_type_label)
        self.geom_type_combo = gui.Combobox()
        self.geom_type_combo.add_item("Point Cloud")
        self.geom_type_combo.add_item("Coordinate Frame")
        self.geom_type_combo.selected_index = 0
        geom_type_row.add_child(self.geom_type_combo)
        geometry_group.add_child(geom_type_row)
        self.widget.add_child(geometry_group)
        self.widget.add_fixed(10)
    

    def set_point_count_label(self, value: int):
        self.point_count_label.text = str(value)
    

    def set_size_label(self, value: float):
        self.size_label.text = f"{value:.2f}"