import json


def save_view_state(path, params):
    with open(path, 'w') as f:
        json.dump(params, f, indent=4)


def load_view_state(path):
    print(f"[Infra] load_camera: path = {path}")
    with open(path, 'r') as f:
        params = json.load(f)
    print(f"[Infra] Loaded camera params with keys: {params.keys()}")
    return params


