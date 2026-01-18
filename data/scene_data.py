import json
import os

structures = []
structure_scales = []
structure_heights = []   # ✅ NEW (Phase B)
active_structure_index = None

SCENE_FILE = os.path.join("data", "scene_snapshot.json")

def get_active_index():
    return active_structure_index

def add_structure(cells, scale=1.0, height=1):
    structures.append(set(cells))
    structure_scales.append(scale)
    structure_heights.append(height)
    set_active_structure(len(structures) - 1)

def add_block_to_structure(index, cell):
    if 0 <= index < len(structures):
        structures[index].add(cell)

def set_active_structure(index):
    global active_structure_index
    if 0 <= index < len(structures):
        active_structure_index = index

def move_structure(index, dx, dy):
    if 0 <= index < len(structures):
        structures[index] = {(x + dx, y + dy) for x, y in structures[index]}

def scale_structure(index, delta):
    if 0 <= index < len(structure_scales):
        structure_scales[index] = max(0.5, min(2.0, structure_scales[index] + delta))

def export_scene():
    os.makedirs(os.path.dirname(SCENE_FILE), exist_ok=True)

    data = []
    for i, s in enumerate(structures):
        data.append({
            "blocks": list(s),
            "scale": structure_scales[i],
            "height": structure_heights[i],
        })

    tmp = SCENE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f)

    try:
        os.replace(tmp, SCENE_FILE)
    except PermissionError:
        pass

def load_scene():
    global active_structure_index

    if not os.path.exists(SCENE_FILE):
        return

    try:
        with open(SCENE_FILE, "r") as f:
            data = json.load(f)
    except:
        return

    structures.clear()
    structure_scales.clear()
    structure_heights.clear()

    for s in data:
        structures.append(set(tuple(b) for b in s["blocks"]))
        structure_scales.append(s.get("scale", 1.0))
        structure_heights.append(s.get("height", 1))

    active_structure_index = 0 if structures else None
