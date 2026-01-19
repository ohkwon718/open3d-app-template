import open3d.visualization.gui as gui
import os


class SettingsPanel:
    def __init__(self, window):
        em = window.theme.font_size
        self._em = em
        separation_height = int(round(0.5 * em))
        self.widget = gui.Vert(0, gui.Margins(0.5 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        self.widget.add_fixed(separation_height)
        
        ######################### View group #########################
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
        self.widget.add_fixed(10)
        
        ######################### Generation group #########################
        generation_group = gui.CollapsableVert("Generation", 0.25 * em, gui.Margins(em, 0, 0, 0))

        # Geometry type selection via tabs (instead of combobox).
        self.geom_type_tabs = gui.TabControl()

        # --- Point Cloud tab (type-specific controls)
        point_cloud_tab = gui.Vert(0.25 * em, gui.Margins(0, 0, 0, 0))
        point_count_row = gui.Horiz(0.25 * em)
        point_count_label = gui.Label("Point Count")
        point_count_row.add_child(point_count_label)
        self.point_count_slider = gui.Slider(gui.Slider.INT)
        self.point_count_slider.set_limits(100, 10000)
        self.point_count_slider.int_value = 10000
        point_count_row.add_child(self.point_count_slider)
        self.point_count_label = gui.Label("10000")
        point_count_row.add_child(self.point_count_label)
        point_cloud_tab.add_child(point_count_row)

        # --- Coordinate Frame tab
        coord_frame_tab = gui.Vert(0.25 * em, gui.Margins(0, 0, 0, 0))
        coord_frame_tab.add_child(gui.Label("Coordinate frame uses the Size slider below."))

        self.geom_type_tabs.add_tab("Point Cloud", point_cloud_tab)
        self.geom_type_tabs.add_tab("Coordinate Frame", coord_frame_tab)
        

        generation_group.add_child(self.geom_type_tabs)
        generation_group.add_fixed(10)

        # Common controls (apply to the selected tab/type)
        generate_row = gui.Horiz(0.25 * em)
        generate_label = gui.Label('Generate')
        generate_row.add_child(generate_label)
        self.generate_button = gui.Button("Generate / Update Geometry")
        generate_row.add_child(self.generate_button)
        generation_group.add_child(generate_row)
        generation_group.add_fixed(10)

        size_row = gui.Horiz(0.25 * em)
        size_label = gui.Label("Geometry Size")
        size_row.add_child(size_label)
        self.size_slider = gui.Slider(gui.Slider.DOUBLE)
        self.size_slider.set_limits(0.1, 5.0)
        self.size_slider.double_value = 1.0
        size_row.add_child(self.size_slider)
        self.size_label = gui.Label("1.0")
        size_row.add_child(self.size_label)
        generation_group.add_child(size_row)

        self.widget.add_child(generation_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)        

        ######################### Cameras group #########################
        cameras_group = gui.CollapsableVert("Cameras", 0.25 * em, gui.Margins(em, 0, 0, 0))
        cameras_group.add_child(gui.Label("Load a view (required) and an optional capture image."))
        cameras_group.add_fixed(6)

        # Camera file pickers (view + capture), styled as: label + text field + "..."
        view_file_row = gui.Horiz()
        view_file_row.add_child(gui.Label("View file"))
        self.selected_view_file_edit = gui.TextEdit()
        self.selected_view_file_edit.text_value = ""
        view_file_row.add_child(self.selected_view_file_edit)
        view_file_row.add_fixed(0.25 * em)
        self.load_view_button = gui.Button("...")
        self.load_view_button.horizontal_padding_em = 0.5
        self.load_view_button.vertical_padding_em = 0
        view_file_row.add_child(self.load_view_button)
        cameras_group.add_child(view_file_row)
        cameras_group.add_fixed(6)

        capture_file_row = gui.Horiz()
        capture_file_row.add_child(gui.Label("Capture file"))
        self.selected_capture_file_edit = gui.TextEdit()
        self.selected_capture_file_edit.text_value = ""
        capture_file_row.add_child(self.selected_capture_file_edit)
        capture_file_row.add_fixed(0.25 * em)
        self.load_capture_button = gui.Button("...")
        self.load_capture_button.horizontal_padding_em = 0.5
        self.load_capture_button.vertical_padding_em = 0
        capture_file_row.add_child(self.load_capture_button)
        cameras_group.add_child(capture_file_row)
        cameras_group.add_fixed(10)

        camera_scale_row = gui.Horiz(0.25 * em)
        camera_scale_row.add_child(gui.Label("Camera Scale"))
        self.camera_scale_slider = gui.Slider(gui.Slider.DOUBLE)
        self.camera_scale_slider.set_limits(0.1, 5.0)
        self.camera_scale_slider.double_value = 1.0
        camera_scale_row.add_child(self.camera_scale_slider)
        self.camera_scale_label = gui.Label("1.0")
        camera_scale_row.add_child(self.camera_scale_label)
        cameras_group.add_child(camera_scale_row)
        cameras_group.add_fixed(10)

        update_cameras_row = gui.Horiz(0.25 * em)
        update_cameras_row.add_child(gui.Label("Update"))
        self.update_cameras_button = gui.Button("Generate / Update Cameras")
        update_cameras_row.add_child(self.update_cameras_button)
        cameras_group.add_child(update_cameras_row)

        self.widget.add_child(cameras_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)
        
        ######################### Geometries group #########################
        geometries_group = gui.CollapsableVert("Geometries", 0.25 * em, gui.Margins(em, 0, 0, 0))
        self.geometry_tree_view = gui.TreeView()
        # NOTE: TreeView uses an internal root item; we attach our items under it.
        self._geometry_tree_root = self.geometry_tree_view.get_root_item()
        geometries_group.add_child(self.geometry_tree_view)
        self.widget.add_child(geometries_group)
        self.widget.add_fixed(10)

        self._geometry_tree_items: dict[str, object] = {}
        self._geometry_tree_cells: dict[str, object] = {}

    def set_point_count_label(self, value: int):
        self.point_count_label.text = str(value)

    def set_size_label(self, value: float):
        self.size_label.text = f"{value:.2f}"

    def set_camera_scale_label(self, value: float):
        self.camera_scale_label.text = f"{value:.2f}"

    def set_selected_view_file(self, path: str | None):
        if path:
            self.selected_view_file_edit.text_value = path
        else:
            self.selected_view_file_edit.text_value = ""

    def set_selected_capture_file(self, path: str | None):
        if path:
            self.selected_capture_file_edit.text_value = path
        else:
            self.selected_capture_file_edit.text_value = ""

    def get_generation_geometry_type(self) -> str:
        """Returns one of: 'point_cloud', 'coordinate_frame' based on the selected tab."""
        idx = getattr(self.geom_type_tabs, "selected_tab_index", 0)
        if idx == 0:
            return "point_cloud"
        return "coordinate_frame"

    def upsert_geometry_toggle(
        self,
        name: str,
        label: str,
        checked: bool,
        on_checked,
    ):
        """
        Adds (or updates) a checkbox row in the Geometries tree.
        `on_checked(checked: bool)` will be called when the checkbox changes.
        """
        # Preferred path: Open3D provides a tree cell with a built-in checkbox + label.
        if hasattr(gui, "CheckableTextTreeCell"):
            cell = self._geometry_tree_cells.get(name)
            if cell is None:
                # Open3D variants differ slightly:
                # - Some require the callback in the constructor: (text, checked, on_checked)
                # - Some allow setting callback after construction.
                try:
                    cell = gui.CheckableTextTreeCell(label, bool(checked), on_checked)
                except TypeError:
                    cell = gui.CheckableTextTreeCell(label, bool(checked))
                    if hasattr(cell, "set_on_checked"):
                        cell.set_on_checked(on_checked)
                    elif hasattr(cell, "set_on_check"):
                        cell.set_on_check(on_checked)

                item = self.geometry_tree_view.add_item(self._geometry_tree_root, cell)
                self._geometry_tree_items[name] = item
                self._geometry_tree_cells[name] = cell
            else:
                if hasattr(cell, "text"):
                    cell.text = label
                if hasattr(cell, "checked"):
                    cell.checked = bool(checked)

                if hasattr(cell, "set_on_checked"):
                    cell.set_on_checked(on_checked)
                elif hasattr(cell, "set_on_check"):
                    cell.set_on_check(on_checked)
            return cell

        # Fallback: if CheckableTextTreeCell isn't available in this Open3D version,
        # keep the UI functional with a regular checkbox row (non-tree).
        # (We still keep this method signature stable for callers.)
        checkbox = gui.Checkbox(label)
        checkbox.checked = bool(checked)
        checkbox.set_on_checked(on_checked)
        return checkbox
