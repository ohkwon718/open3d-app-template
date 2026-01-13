import json


def save_view_state(path, params):
    with open(path, 'w') as f:
        json.dump(params, f, indent=4)


def load_view_state(path):
    with open(path, 'r') as f:
        params = json.load(f)
    return params
