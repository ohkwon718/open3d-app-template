import open3d.visualization.gui as gui
import os


class SettingsPanel:
    def __init__(self, window):
        self._window = window
        em = window.theme.font_size
        self._em = em
        separation_height = int(round(0.5 * em))

        def _style_button(btn: gui.Button):
            # Keep all buttons visually consistent (especially height).
            btn.horizontal_padding_em = 0.5
            btn.vertical_padding_em = 0
            return btn

        self.widget = gui.Vert(0, gui.Margins(0.5 * em, 0.25 * em, 0.25 * em, 0.25 * em))
        self.widget.add_fixed(separation_height)
        
        ######################### View group #########################
        view_group = gui.CollapsableVert("View", 0.25 * em, gui.Margins(em, 0, 0, 0))
        screenshot_row = gui.Horiz(0.25 * em)
        screenshot_label = gui.Label('Screenshot')
        screenshot_row.add_child(screenshot_label)
        self.screenshot_button = _style_button(gui.Button("Save"))
        screenshot_row.add_child(self.screenshot_button)
        view_group.add_child(screenshot_row)
        
        camera_label = gui.Label('Camera View')
        view_group.add_child(camera_label)
        
        camera_row = gui.Horiz(0.25 * em)
        self.save_camera_button = _style_button(gui.Button("Save"))
        camera_row.add_child(self.save_camera_button)
        self.load_camera_button = _style_button(gui.Button("Load"))
        camera_row.add_child(self.load_camera_button)
        self.load_latest_camera_button = _style_button(gui.Button("Load Latest"))
        camera_row.add_child(self.load_latest_camera_button)
        view_group.add_child(camera_row)
        self.widget.add_child(view_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)

        ######################### Scene group #########################
        scene_group = gui.CollapsableVert("Scene", 0.25 * em, gui.Margins(em, 0, 0, 0))
        self.black_background_checkbox = gui.Checkbox("Black background")
        self.black_background_checkbox.checked = True
        scene_group.add_child(self.black_background_checkbox)
        self.widget.add_child(scene_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)
        
        ######################### Geometry group #########################
        geometry_group = gui.CollapsableVert("Geometry", 0.25 * em, gui.Margins(em, 0, 0, 0))

        ply_row = gui.Horiz(0.25 * em)
        ply_row.add_child(gui.Label("Ply"))
        self.import_ply_button = _style_button(gui.Button("Import"))
        ply_row.add_child(self.import_ply_button)
        geometry_group.add_child(ply_row)
        geometry_group.add_fixed(10)

        point_count_row = gui.Horiz(0.25 * em)
        point_count_label = gui.Label("Point Count")
        point_count_row.add_child(point_count_label)
        self.point_count_slider = gui.Slider(gui.Slider.INT)
        self.point_count_slider.set_limits(100, 10000)
        self.point_count_slider.int_value = 10000
        point_count_row.add_child(self.point_count_slider)
        geometry_group.add_child(point_count_row)
        geometry_group.add_fixed(10)

        size_row = gui.Horiz(0.25 * em)
        size_label = gui.Label("Point Cloud Size")
        size_row.add_child(size_label)
        self.size_slider = gui.Slider(gui.Slider.DOUBLE)
        self.size_slider.set_limits(0.1, 5.0)
        self.size_slider.double_value = 1.0
        size_row.add_child(self.size_slider)
        geometry_group.add_child(size_row)
        geometry_group.add_fixed(10)

        self.generate_button = _style_button(gui.Button("Update Point Cloud"))
        geometry_group.add_child(self.generate_button)

        self.widget.add_child(geometry_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)        

        ######################### Cameras group #########################
        cameras_group = gui.CollapsableVert("Cameras", 0.25 * em, gui.Margins(em, 0, 0, 0))
        
        camera_scale_row = gui.Horiz(0.25 * em)
        camera_scale_row.add_child(gui.Label("Camera Scale"))
        self.camera_scale_slider = gui.Slider(gui.Slider.DOUBLE)
        self.camera_scale_slider.set_limits(0.1, 5.0)
        self.camera_scale_slider.double_value = 1.0
        camera_scale_row.add_child(self.camera_scale_slider)
        cameras_group.add_child(camera_scale_row)
        cameras_group.add_fixed(10)

        self.add_camera_from_scene_button = _style_button(gui.Button("Add from scene"))
        cameras_group.add_child(self.add_camera_from_scene_button)
        cameras_group.add_fixed(6)

        self.update_cameras_button = _style_button(gui.Button("Add from files"))
        cameras_group.add_child(self.update_cameras_button)
        cameras_group.add_fixed(10)

        view_file_row = gui.Horiz()
        view_file_row.add_child(gui.Label("View file"))
        self.selected_view_file_edit = gui.TextEdit()
        self.selected_view_file_edit.text_value = ""
        view_file_row.add_child(self.selected_view_file_edit)
        view_file_row.add_fixed(0.25 * em)
        self.load_view_button = _style_button(gui.Button("..."))
        view_file_row.add_child(self.load_view_button)
        cameras_group.add_child(view_file_row)
        cameras_group.add_fixed(6)

        capture_file_row = gui.Horiz()
        capture_file_row.add_child(gui.Label("Capture file"))
        self.selected_capture_file_edit = gui.TextEdit()
        self.selected_capture_file_edit.text_value = ""
        capture_file_row.add_child(self.selected_capture_file_edit)
        capture_file_row.add_fixed(0.25 * em)
        self.load_capture_button = _style_button(gui.Button("..."))
        capture_file_row.add_child(self.load_capture_button)
        cameras_group.add_child(capture_file_row)
        cameras_group.add_fixed(10)

        cameras_group.add_child(gui.Label("Current cameras"))
        self.cameras_tree_view = gui.TreeView()
        self._cameras_tree_root = self.cameras_tree_view.get_root_item()
        cameras_group.add_child(self.cameras_tree_view)
        cameras_group.add_fixed(6)

        self.rerender_camera_images_button = _style_button(gui.Button("Rerender camera images"))
        cameras_group.add_child(self.rerender_camera_images_button)
        cameras_group.add_fixed(6)

        # Keep actions visually consistent: use simple buttons (no extra labels).
        self.delete_selected_camera_button = _style_button(gui.Button("Delete selected camera"))
        cameras_group.add_child(self.delete_selected_camera_button)
        cameras_group.add_fixed(6)

        export_row = gui.Horiz(0.25 * em)
        self.export_camera_set_button = _style_button(gui.Button("Export camera set"))
        export_row.add_child(self.export_camera_set_button)
        self.import_camera_set_button = _style_button(gui.Button("Import camera set"))
        export_row.add_child(self.import_camera_set_button)
        cameras_group.add_child(export_row)

        self.widget.add_child(cameras_group)
        self.widget.add_fixed(separation_height)
        self.widget.add_fixed(10)
        
        ######################### Visibility group #########################
        visibility_group = gui.CollapsableVert("Visibility", 0.25 * em, gui.Margins(em, 0, 0, 0))
        self.visibility_tree_view = gui.TreeView()
        # NOTE: TreeView uses an internal root item; we attach our items under it.
        self._visibility_tree_root = self.visibility_tree_view.get_root_item()
        visibility_group.add_child(self.visibility_tree_view)
        visibility_group.add_fixed(6)

        cameras_visibility_row = gui.Horiz(0.25 * em)
        cameras_visibility_row.add_child(gui.Label("Cameras"))
        self.show_all_cameras_button = _style_button(gui.Button("Show all"))
        cameras_visibility_row.add_child(self.show_all_cameras_button)
        self.hide_all_cameras_button = _style_button(gui.Button("Hide all"))
        cameras_visibility_row.add_child(self.hide_all_cameras_button)
        visibility_group.add_child(cameras_visibility_row)

        self.widget.add_child(visibility_group)
        self.widget.add_fixed(10)

        self._visibility_tree_items: dict[str, object] = {}
        self._visibility_tree_cells: dict[str, object] = {}
        self._visibility_tree_item_to_name: dict[object, str] = {}
        self._selected_visibility_name: str | None = None

        self._camera_tree_items: dict[int, object] = {}
        self._camera_tree_item_to_index: dict[object, int] = {}
        self._selected_camera_index: int | None = None

        # Optional callback set by MainWindow.
        self._on_delete_geometry_requested = None
        self._on_delete_camera_requested = None

        # Track selection if supported by this Open3D build.
        if hasattr(self.visibility_tree_view, "set_on_selection_changed"):
            def _on_selection_changed(*args):
                # Different Open3D versions pass different args; we rely on our mapping.
                item = args[-1] if args else None
                self._selected_visibility_name = self._visibility_tree_item_to_name.get(item, None)
            self.visibility_tree_view.set_on_selection_changed(_on_selection_changed)

        if hasattr(self.cameras_tree_view, "set_on_selection_changed"):
            def _on_camera_selection_changed(*args):
                item = args[-1] if args else None
                self._selected_camera_index = self._camera_tree_item_to_index.get(item, None)
            self.cameras_tree_view.set_on_selection_changed(_on_camera_selection_changed)

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

    def set_on_delete_geometry_requested(self, callback):
        """callback(name: str) -> None"""
        self._on_delete_geometry_requested = callback

    def set_on_delete_camera_requested(self, callback):
        """callback(idx: int) -> None"""
        self._on_delete_camera_requested = callback

    def _request_delete_geometry(self, name: str):
        # If the app didn't set a delete callback yet, do nothing.
        if self._on_delete_geometry_requested is None:
            return
        self._on_delete_geometry_requested(name)

    def _request_delete_camera(self, idx: int):
        if self._on_delete_camera_requested is None:
            return
        self._on_delete_camera_requested(idx)

    def get_selected_geometry_name(self) -> str | None:
        return self._selected_visibility_name

    def get_selected_camera_index(self) -> int | None:
        return self._selected_camera_index

    def list_visibility_names(self) -> list[str]:
        return list(self._visibility_tree_items.keys())

    def upsert_camera_item(self, idx: int, label: str | None = None):
        if label is None:
            label = f"Camera {idx}"
        item = self._camera_tree_items.get(idx)
        if item is None:
            # Use a plain text item for broad compatibility.
            if hasattr(self.cameras_tree_view, "add_text_item"):
                item = self.cameras_tree_view.add_text_item(self._cameras_tree_root, label)
            else:
                # Fallback: use a checkable cell as text-only (checked state irrelevant here)
                cell = gui.CheckableTextTreeCell(label, True, lambda _: None) if hasattr(gui, "CheckableTextTreeCell") else gui.Label(label)
                item = self.cameras_tree_view.add_item(self._cameras_tree_root, cell)
            self._camera_tree_items[idx] = item
            self._camera_tree_item_to_index[item] = idx
        else:
            # Best-effort rename if API supports it; otherwise leave as-is.
            pass

    def remove_camera_item(self, idx: int):
        item = self._camera_tree_items.get(idx)
        if item is not None and hasattr(self.cameras_tree_view, "remove_item"):
            try:
                self.cameras_tree_view.remove_item(item)
            except Exception:
                pass
        self._camera_tree_items.pop(idx, None)
        if item is not None:
            self._camera_tree_item_to_index.pop(item, None)
        if self._selected_camera_index == idx:
            self._selected_camera_index = None

    def list_camera_indices(self) -> list[int]:
        return sorted(self._camera_tree_items.keys())

    def remove_geometry_toggle(self, name: str):
        # Remove a row from the TreeView and internal mappings.
        item = self._visibility_tree_items.get(name)
        if item is not None and hasattr(self.visibility_tree_view, "remove_item"):
            try:
                self.visibility_tree_view.remove_item(item)
            except Exception:
                pass
        self._visibility_tree_items.pop(name, None)
        self._visibility_tree_cells.pop(name, None)
        if item is not None:
            self._visibility_tree_item_to_name.pop(item, None)
        if self._selected_visibility_name == name:
            self._selected_visibility_name = None

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
            cell = self._visibility_tree_cells.get(name)
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

                item = self.visibility_tree_view.add_item(self._visibility_tree_root, cell)
                self._visibility_tree_items[name] = item
                self._visibility_tree_cells[name] = cell
                self._visibility_tree_item_to_name[item] = name
            else:
                if hasattr(cell, "text"):
                    cell.text = label
                # Note: we don't try to programmatically sync checkmarks. The checkmark
                # reflects user interaction; bulk show/hide buttons affect scene only.

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
