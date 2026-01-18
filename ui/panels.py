import open3d.visualization.gui as gui
import os


class SettingsPanel:
    def __init__(self, window):
        em = window.theme.font_size
        self._em = em
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
        self.widget.add_fixed(10)
        
        generation_group = gui.CollapsableVert("Generation", 0.25 * em, gui.Margins(em, 0, 0, 0))
        geom_type_row = gui.Horiz(0.25 * em)
        geom_type_label = gui.Label("Geometry Type")
        geom_type_row.add_child(geom_type_label)
        self.geom_type_combo = gui.Combobox()
        self.geom_type_combo.add_item("Point Cloud")
        self.geom_type_combo.add_item("Coordinate Frame")
        self.geom_type_combo.add_item("Cameras")
        self.geom_type_combo.selected_index = 0
        geom_type_row.add_child(self.geom_type_combo)
        generation_group.add_child(geom_type_row)
        generation_group.add_fixed(10)
        
        generate_row = gui.Horiz(0.25 * em)
        generate_label = gui.Label('Generate')
        generate_row.add_child(generate_label)
        self.generate_button = gui.Button("Generate / Update Geometry")
        generate_row.add_child(self.generate_button)
        generation_group.add_child(generate_row)
        generation_group.add_fixed(10)
        
        point_count_row = gui.Horiz(0.25 * em)
        point_count_label = gui.Label("Point Count")
        point_count_row.add_child(point_count_label)
        self.point_count_slider = gui.Slider(gui.Slider.INT)
        self.point_count_slider.set_limits(100, 10000)
        self.point_count_slider.int_value = 10000
        point_count_row.add_child(self.point_count_slider)
        self.point_count_label = gui.Label("10000")
        point_count_row.add_child(self.point_count_label)
        generation_group.add_child(point_count_row)
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
        generation_group.add_fixed(10)
        
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
        generation_group.add_child(view_file_row)
        generation_group.add_fixed(6)

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
        generation_group.add_child(capture_file_row)
        self.widget.add_child(generation_group)
        self.widget.add_fixed(10)
        
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
