# Open3D App Template

A minimal, clone-and-go template for building Open3D-based GUI applications.

This repository is intentionally minimal and direct—no frameworks, no unnecessary abstractions. Just Open3D and practical helpers to get you started quickly.

## Philosophy

**Minimal, direct, practical.** Use Open3D directly. Split files for clarity, not for architectural theory.

## Usage

1. Clone this repository
2. Remove the `.git` directory
3. Start building your own Open3D-based application

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```

## Repository Structure

```
open3d-app-template/
├─ README.md
├─ main.py              # Entry point
├─ ui/                  # UI components
│  ├─ __init__.py
│  ├─ main_window.py    # Main window and callbacks
│  ├─ scene_view.py     # 3D scene widget wrapper
│  └─ panels.py         # Settings panel UI
├─ tools/               # Reusable helpers
│  ├─ __init__.py
│  ├─ camera_math.py    # Camera matrix utilities
│  ├─ camera_set_io.py  # Export/import camera sets (JSON + images)
│  ├─ camera_view_io.py # Save/load Open3D GUI camera view state
│  ├─ camera_viz.py     # Camera visualization helpers
│  ├─ screenshot.py     # Screenshot capture/save
├─ samples/             # Optional demo data
│  └─ train/
└─ requirements.txt
```

## Code Organization

### `main.py`

Simple entry point that initializes the Open3D application and creates the main window.

### `ui/main_window.py`

Main window class that:
- Creates and manages the window layout
- Owns `SceneWidget` and `SettingsPanel`
- Handles UI callbacks and user interactions
- Contains example geometry generation helpers

### `ui/scene_view.py`

Wrapper around Open3D's `SceneWidget` that provides:
- Geometry add/update/remove operations
- Camera setup and view state management
- Image capture functionality

### `ui/panels.py`

Settings panel UI component with:
- Screenshot and camera view controls
- Point cloud generation controls (as a sample geometry)
- Camera controls (add, delete, export/import)
- Visibility toggles

### `tools/`

Small, reusable helper functions:
- **`camera_math.py`** - Camera matrix transformations (intrinsic/extrinsic)
- **`camera_set_io.py`** - Export/import camera sets (JSON + images)
- **`camera_view_io.py`** - Save/load Open3D GUI camera view state (`model_matrix`, `width`, `height`)
- **`camera_viz.py`** - Camera visualization geometry helpers
- **`screenshot.py`** - Screenshot capture and save utilities

## Camera features

- **Add cameras**: add a camera frustum (+ optional image plane) from:
  - current scene camera (**Add from scene**)
  - a saved view + image (**Add from files**)
- **Visibility**: toggle per-geometry visibility and show/hide all camera geometries.
- **Camera sets**: export/import camera sets to/from `export/camera_sets/<timestamp>/`:
  - `cameras.json`
  - `images/cam_###.png` (only when a camera has an image)

## Todo

- [ ] Demo Clip


## Notes

- This template favors clarity over cleverness.
- No app/service/domain/controller layers—just direct Open3D usage.
- File splitting is for readability, not architectural theory.
- Keep it simple and practical.
