from dataclasses import dataclass


@dataclass
class AppState:
    point_count: int = 1000
    geometry_size: float = 1.0
    geometry_type: str = "point_cloud"
