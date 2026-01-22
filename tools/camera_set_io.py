import json
import os
from datetime import datetime
from typing import Any

import numpy as np
import open3d as o3d

from tools.screenshot import save_image


def make_camera_record(
    *,
    source: str,
    width: int,
    height: int,
    model_matrix: np.ndarray,
    extrinsic: np.ndarray,
    intrinsic: o3d.camera.PinholeCameraIntrinsic,
    image_path: str | None = None,
    image_array: np.ndarray | None = None,
) -> dict[str, Any]:
    """Create a serializable camera record used by export/import."""
    width_i = int(width)
    height_i = int(height)
    model_matrix = np.asarray(model_matrix, dtype=np.float64)
    extrinsic = np.asarray(extrinsic, dtype=np.float64)

    fx, fy = intrinsic.get_focal_length()
    cx, cy = intrinsic.get_principal_point()
    K = np.asarray(intrinsic.intrinsic_matrix)

    return {
        "source": source,
        "width": width_i,
        "height": height_i,
        # Keep compatibility with export/views format
        "model_matrix": model_matrix.tolist(),
        # Alias for clarity
        "c2w": model_matrix.tolist(),
        "extrinsic": extrinsic.tolist(),
        "intrinsic": {
            "width": width_i,
            "height": height_i,
            "fx": float(fx),
            "fy": float(fy),
            "cx": float(cx),
            "cy": float(cy),
            "K": K.tolist(),
        },
        "image_path": image_path,
        "image_array": image_array,
    }


def export_camera_set(
    *,
    indices: list[int],
    camera_records: dict[int, dict[str, Any]],
    export_root: str = "export/camera_sets",
) -> str:
    """
    Export to:
      export/camera_sets/<timestamp>/
        cameras.json
        images/cam_###.png

    Returns absolute output directory path.
    """
    if not indices:
        raise ValueError("No camera indices to export")

    ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    out_dir = os.path.abspath(os.path.join(export_root, ts))
    images_dir = os.path.join(out_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    cameras_out: list[dict[str, Any]] = []
    for idx in indices:
        rec = camera_records.get(idx)
        if rec is None:
            continue

        entry: dict[str, Any] = {
            "id": int(idx),
            "source": rec.get("source"),
            "width": rec.get("width"),
            "height": rec.get("height"),
            "model_matrix": rec.get("model_matrix"),
            "c2w": rec.get("c2w"),
            "extrinsic": rec.get("extrinsic"),
            "intrinsic": rec.get("intrinsic"),
        }

        image_rel = None
        image_path = rec.get("image_path")
        image_array = rec.get("image_array")
        out_png = os.path.join(images_dir, f"cam_{idx:03d}.png")

        if isinstance(image_array, np.ndarray):
            img_o3d = o3d.geometry.Image(image_array)
            save_image(out_png, img_o3d)
            image_rel = os.path.relpath(out_png, out_dir)
        elif isinstance(image_path, str) and os.path.exists(image_path):
            img_o3d = o3d.io.read_image(image_path)
            save_image(out_png, img_o3d)
            image_rel = os.path.relpath(out_png, out_dir)

        if image_rel is not None:
            entry["image_file"] = image_rel

        cameras_out.append(entry)

    payload = {
        "version": 1,
        "created_at": ts,
        "root_format": "open3d_gui_view_state",
        "cameras": cameras_out,
    }

    json_path = os.path.join(out_dir, "cameras.json")
    with open(json_path, "w") as f:
        json.dump(payload, f, indent=2)

    return out_dir


def load_camera_set(json_path: str) -> tuple[dict[str, Any], str]:
    """Loads cameras.json and returns (payload, base_dir)."""
    abs_path = os.path.abspath(json_path)
    with open(abs_path, "r") as f:
        payload = json.load(f)
    return payload, os.path.dirname(abs_path)


def load_camera_image_array(base_dir: str, image_file: str | None) -> tuple[np.ndarray | None, str | None]:
    if not image_file:
        return None, None
    image_path = os.path.join(base_dir, image_file)
    if not os.path.exists(image_path):
        return None, None
    img_o3d = o3d.io.read_image(image_path)
    return np.asarray(img_o3d), image_path

