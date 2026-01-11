# Open3D App Template

A reusable template for building Open3D-based GUI applications with a clean separation between:

- **UI composition**
- **interaction logic**
- **visualization**
- **core application logic**

The repository is intentionally minimal and opinionated, designed as a learning reference for structuring Open3D GUI software.

## Philosophy

**Views render. Controllers decide. App executes. Domain computes.**

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
├─ main.py
├─ ui/
│  ├─ __init__.py
│  ├─ main_window.py
│  ├─ scene_view.py
│  └─ panels.py
├─ controllers/
│  ├─ __init__.py
│  └─ interaction_controller.py
├─ app/
│  ├─ __init__.py
│  ├─ app_service.py
│  └─ app_state.py
├─ domain/
│  ├─ __init__.py
│  ├─ example_logic.py
│  └─ camera_math.py
├─ viz/
│  ├─ __init__.py
│  └─ geometry_factory.py
├─ vis/
│  └─ geometry_factory.py
├─ infra/
│  ├─ __init__.py
│  ├─ image_io.py
│  └─ view_io.py
└─ requirements.txt
```

## Architecture

### `main.py` — Composition Root

- Creates `AppService`
- Creates `MainWindow`
- Creates `InteractionController`
- Wires dependencies
- Starts the GUI loop

### `ui/main_window.py`

**Purpose:** UI composition & layout

- Window creation
- Layout (content_rect, frames)
- Ownership of `SceneView` and `SettingsPanel`
- `run()` method

### `ui/scene_view.py`

**Purpose:** Visualization wrapper

- Ownership of `gui.SceneWidget`
- `add/update/remove_geometry(...)`
- Camera/view helpers

### `ui/panels.py`

**Purpose:** Panel UI only

- Buttons, sliders, checkboxes
- Internal layout of the panel

### `controllers/interaction_controller.py`

**Purpose:** Bridge between UI and app

- References to `SceneView`, `SettingsPanel`, `AppService`
- UI callbacks (`on_button_clicked`, `on_slider_changed`)
- Calls to app use-cases

**This is the only UI-side class allowed to call `AppService`.**

### `app/app_service.py`

**Purpose:** Application use-cases

- User-intent methods (`run_example`, `load_data`, etc.)
- Coordination logic
- State updates
- Event/callback mechanism

### `app/app_state.py`

**Purpose:** Single source of truth

- Simple data (dataclass-style)
- No behavior
- No Open3D types if possible

### `domain/example_logic.py`

**Purpose:** Pure logic example

- Small, testable functions (e.g., generate points, transform poses)
- No Open3D GUI
- No app/service code

### `viz/geometry_factory.py`

**Purpose:** Open3D object construction

- Functions that convert data → `o3d.geometry.*`
- Camera frustum / axes example
- No `SceneWidget`
- No `add_geometry()`

### `domain/camera_math.py`

**Purpose:** Camera-related mathematical utilities

- Camera matrix transformations
- Intrinsic/extrinsic matrix helpers

### `infra/`

**Purpose:** Infrastructure utilities

- Image I/O operations
- View I/O operations

## Todo

- [ ] Virtual Camera Visualization


## Notes

This template favors clarity over cleverness.
