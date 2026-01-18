import cv2
import mediapipe as mp
import math
import ctypes
import time
import json 
from data.scene_data import (
    structures,
    structure_scales,
    structure_heights,
    get_active_index,
    set_active_structure,
    add_structure,
    move_structure,
    scale_structure,
    export_scene,
)

# ================== FULLSCREEN ==================
user32 = ctypes.windll.user32
SCREEN_W = user32.GetSystemMetrics(0)
SCREEN_H = user32.GetSystemMetrics(1)

# ================== MEDIAPIPE ==================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)
cap = cv2.VideoCapture(1)

# ================== GRID & MODES ==================
GRID_SIZE = 40
MODES = ["BUILD", "SCALE", "GROUP", "EXTRUDE"]
mode = "BUILD"

# Grid colors (Not used anymore, but kept for reference if needed, or can be removed)
# GRID_COLOR = (0, 0, 255)      
# GRID_GLOW_COLOR = (0, 0, 180) 

# Active structure outline color (Added Step 1)
ACTIVE_OUTLINE_COLOR = (255, 255, 0)  # cyan (BGR)

# Menu hover color (Added Step 1)
MENU_HOVER_COLOR = (255, 255, 0)   # cyan

# ================== MENU UI ==================
MENU_X = 20
MENU_Y = 80
MENU_W = 160
MENU_H = 50

# ================== PHASE A ==================
DRAW_HOLD_TIME = 0.5
hold_start = None
blueprint_active = False
blueprint_start_cell = None
blueprint_cells = set()
blueprint_outline = set()
blueprint_axis = None

# ================== PHASE B ==================
last_extrude_y = None
MAX_HEIGHT = 20

# ================== PHASE C ==================
ghost_height = None
show_height_hud = False

# ================== PHASE D.1 ==================
two_hand_hold_start = None
two_hand_ready = False
# CHANGE 1: Global Lock Flag
editor_locked = False

fist_hold_start = None
fist_locked = False
fist_move_active = False
move_anchor_hand = None
move_anchor_cells = None

# ================== STATE ==================
last_pinch = False
# (REMOVED UNUSED D.2 STATE VARIABLES HERE)
# STEP 2: GROUP selection state
group_select_locked = False

# STEP 1: Commit feedback
commit_message = None
commit_time = 0
COMMIT_DISPLAY_TIME = 0.5  # seconds

# ================== UNDO / REDO ==================
undo_stack = []
redo_stack = []
MAX_HISTORY = 30

# ================== HELPERS ==================

# (REMOVED EXPORT_TRANSFORM HELPER HERE)

# --- UNDO / REDO HELPERS (STEP 2) ---
def snapshot_scene():
    return {
        "structures": [set(s) for s in structures],
        "scales": list(structure_scales),
        "heights": list(structure_heights),
        "active": get_active_index()
    }

def restore_scene(snap):
    structures[:] = [set(s) for s in snap["structures"]]
    structure_scales[:] = snap["scales"]
    structure_heights[:] = snap["heights"]
    set_active_structure(snap["active"])
    export_scene()

def push_undo():
    undo_stack.append(snapshot_scene())
    if len(undo_stack) > MAX_HISTORY:
        undo_stack.pop(0)
    redo_stack.clear()
# ------------------------------------

# STEP 2: Trigger feedback helper
def trigger_commit(msg):
    global commit_message, commit_time
    commit_message = msg
    commit_time = time.time()

def finger_extended(lm, tip, pip):
    return lm[tip].y < lm[pip].y

def distance(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

def is_fist(lm):
    return not any([
        finger_extended(lm, 8, 6),
        finger_extended(lm, 12, 10),
        finger_extended(lm, 16, 14),
        finger_extended(lm, 20, 18),
    ])

def has_valid_active_structure():
    idx = get_active_index()
    return idx is not None and 0 <= idx < len(structures)

# STEP 1: Helper function
def get_structure_at_cell(cell):
    """
    Returns index of structure that contains the given grid cell.
    If none found, returns None.
    """
    for i, s in enumerate(structures):
        if cell in s:
            return i
    return None

def rect_cells(a, b):
    x1, y1 = a
    x2, y2 = b
    return {(x, y) for x in range(min(x1, x2), max(x1, x2) + 1)
                    for y in range(min(y1, y2), max(y1, y2) + 1)}

def rect_outline_cells(a, b):
    x1, y1 = a
    x2, y2 = b
    cells = set()
    for x in range(min(x1, x2), max(x1, x2) + 1):
        cells.add((x, y1))
        cells.add((x, y2))
    for y in range(min(y1, y2), max(y1, y2) + 1):
        cells.add((x1, y))
        cells.add((x2, y))
    return cells

# --- REPLACED FUNCTION (P1.2 - Hologram) ---
def draw_blueprint_block(frame, x, y, size, t=time.time()):
    # PART 1: CHANGED COLORS (FIXED CYAN BGR)
    base_color = (255, 255, 0)   # cyan fill (BGR)
    edge_color = (255, 200, 0)   # cyan edge

    # Subtle parallax (based on time, not input)
    parallax = int(3 * math.sin(t * 2))
    y += parallax

    # Translucent fill
    overlay = frame.copy()
    cv2.rectangle(overlay, (x, y), (x + size, y + size), base_color, -1)
    cv2.addWeighted(overlay, 0.16, frame, 0.84, 0, frame)

    # Outline
    cv2.rectangle(frame, (x, y), (x + size, y + size), edge_color, 2)

    # X brace
    cv2.line(frame, (x, y), (x + size, y + size), edge_color, 1)
    cv2.line(frame, (x + size, y), (x, y + size), edge_color, 1)

    # Hologram scanlines
    scan_y = int((t * 80) % size)
    for sy in range(y + scan_y, y + size, 12):
        cv2.line(frame, (x, sy), (x + size, sy), (0, 220, 220), 1)
# -------------------------------

# ================== AUTO MERGE ==================
def cells_touch(a, b):
    for (x, y) in a:
        for dx, dy in [(0,0),(1,0),(-1,0),(0,1),(0,-1)]:
            if (x + dx, y + dy) in b:
                return True
    return False

def auto_merge_structures():
    merged = []
    merged_scales = []
    merged_heights = []

    for i, s in enumerate(structures):
        merged_into = False
        for j, ms in enumerate(merged):
            if cells_touch(s, ms):
                merged[j] |= s
                merged_heights[j] = max(merged_heights[j], structure_heights[i])
                merged_into = True
                break
        if not merged_into:
            merged.append(set(s))
            merged_scales.append(structure_scales[i])
            merged_heights.append(structure_heights[i])

    structures[:] = merged
    structure_scales[:] = merged_scales
    structure_heights[:] = merged_heights

# ================== WINDOW ==================
cv2.namedWindow("AirBlocks", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("AirBlocks", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# ================== MAIN LOOP ==================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # CHANGE: Define hovered_index at top of loop
    hovered_index = None

    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (SCREEN_W, SCREEN_H))
    h, w, _ = frame.shape

    result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    pinch = False
    open_hand = False
    cursor_cell = None

    if result.multi_hand_landmarks:

        # ===== TWO HAND READY =====
        open_hands = 0
        pinch_seen = False
        for hlm in result.multi_hand_landmarks:
            lm = hlm.landmark
            if all(finger_extended(lm, t, p) for t,p in [(8,6),(12,10),(16,14),(20,18)]):
                open_hands += 1
            if distance(lm[4], lm[8]) < 0.05:
                pinch_seen = True

        if open_hands == 2 and not pinch_seen and not two_hand_ready:
            if two_hand_hold_start is None:
                two_hand_hold_start = time.time()
            progress = min((time.time()-two_hand_hold_start)/DRAW_HOLD_TIME,1)
            cv2.ellipse(frame,(SCREEN_W//2,SCREEN_H//2),(40,40),
                        0,0,int(360*progress),(0,255,255),3)
            # CHANGE 2: Lock Editor
            if progress >= 1:
                two_hand_ready = True
                editor_locked = True
        else:
            # CHANGE 3: Unlock Editor
            two_hand_hold_start = None
            if two_hand_ready and open_hands < 2:
                two_hand_ready = False
                editor_locked = False

        # ===== PRIMARY HAND =====
        lmks = result.multi_hand_landmarks[0]
        mp_draw.draw_landmarks(frame, lmks, mp_hands.HAND_CONNECTIONS)
        lm = lmks.landmark

        open_hand = all(finger_extended(lm, t, p) for t,p in [(8,6),(12,10),(16,14),(20,18)])
        pinch = distance(lm[4], lm[8]) < 0.05
        fist = is_fist(lm)

        ix, iy = int(lm[8].x * w), int(lm[8].y * h)
        cursor_cell = (ix // GRID_SIZE, iy // GRID_SIZE)
        cv2.circle(frame, (ix, iy), 6, (0,255,255), -1)

        # STEP 3: ===== GROUP MODE: STRUCTURE SELECTION =====
        if mode == "GROUP":
            if pinch and not group_select_locked:
                hit = get_structure_at_cell(cursor_cell)
                if hit is not None:
                    set_active_structure(hit)
                    group_select_locked = True
            if not pinch:
                group_select_locked = False

        # ===== FIST MOVE WITH LOADER =====
        # CHANGE 4.2: Add 'and not editor_locked'
        if fist and not blueprint_active and has_valid_active_structure() and not editor_locked:
            if not fist_locked:
                if fist_hold_start is None:
                    fist_hold_start = time.time()
                progress = min((time.time()-fist_hold_start)/DRAW_HOLD_TIME,1)
                cv2.ellipse(frame,(ix,iy),(28,28),
                            0,0,int(360*progress),(0,255,255),2)
                if progress >= 1:
                    fist_locked = True
                    fist_move_active = True
                    move_anchor_hand = cursor_cell
                    move_anchor_cells = set(structures[get_active_index()])
            else:
                dx = cursor_cell[0] - move_anchor_hand[0]
                dy = cursor_cell[1] - move_anchor_hand[1]
                structures[get_active_index()] = {
                    (x+dx,y+dy) for x,y in move_anchor_cells
                }
        else:
            # STEP 3.2: FIST RELEASE UNDO
            if fist_move_active:
                push_undo()
                export_scene()
                trigger_commit("MOVE OK") # STEP 3: Trigger Feedback
            fist_hold_start = None
            fist_locked = False
            fist_move_active = False

        # ===== MENU =====
        # CHANGE: Removed redundant hovered_index = None here
        for i,m in enumerate(MODES):
            y = MENU_Y + i*MENU_H
            if MENU_X < ix < MENU_X+MENU_W and y < iy < y+MENU_H:
                hovered_index = i

        if pinch and hovered_index is not None and not last_pinch:
            mode = MODES[hovered_index]
            last_pinch = True
        if not pinch:
            last_pinch = False

        # ===== BUILD =====
        if mode == "BUILD" and not two_hand_ready:
            if pinch and not blueprint_active:
                if hold_start is None:
                    hold_start = time.time()
                progress = min((time.time()-hold_start)/DRAW_HOLD_TIME,1)
                cv2.ellipse(frame,(ix,iy),(28,28),
                            0,0,int(360*progress),(0,255,255),2)
                if progress >= 1:
                    blueprint_active = True
                    blueprint_start_cell = cursor_cell
                    blueprint_axis = None

            elif blueprint_active and pinch:
                sx,sy = blueprint_start_cell
                cx,cy = cursor_cell
                blueprint_axis = "H" if abs(cx-sx)>=abs(cy-sy) else "V"
                end = (cx,sy) if blueprint_axis=="H" else (sx,cy)
                blueprint_cells = rect_cells(blueprint_start_cell,end)
                blueprint_outline = rect_outline_cells(blueprint_start_cell,end)

            # CHANGE 4.1: Add 'and not editor_locked'
            elif blueprint_active and open_hand and not editor_locked:
                # STEP 3.1: BUILD COMMIT UNDO
                push_undo()
                add_structure(blueprint_cells,1.0,1)
                auto_merge_structures()
                set_active_structure(len(structures)-1)
                export_scene()
                trigger_commit("BUILD OK") # STEP 3: Trigger Feedback
                blueprint_active=False
                blueprint_cells.clear()
                blueprint_outline.clear()
                hold_start=None

            if not pinch:
                hold_start=None

        # ===== EXTRUDE =====
        # CHANGE 4.3: Add 'and not editor_locked'
        if mode=="EXTRUDE" and has_valid_active_structure() and not editor_locked:
            idx=get_active_index()
            if pinch:
                show_height_hud=True
                if last_extrude_y is None:
                    last_extrude_y=iy
                    ghost_height=structure_heights[idx]
                if abs(last_extrude_y-iy)>10:
                    structure_heights[idx]=max(1,min(MAX_HEIGHT,
                        ghost_height+(1 if iy<last_extrude_y else -1)))
                    ghost_height=structure_heights[idx]
                    last_extrude_y=iy
            else:
                # STEP 3.3: EXTRUDE RELEASE UNDO
                if last_extrude_y is not None:
                    push_undo()
                    export_scene()
                    trigger_commit("EXTRUDE OK") # STEP 3: Trigger Feedback
                last_extrude_y=None
                ghost_height=None
                show_height_hud=False

    # ===== DRAW BLUEPRINT (AR STYLE) - REPLACED (STEP 2) =====
    for x, y in blueprint_cells:
        px = x * GRID_SIZE
        py = y * GRID_SIZE
        # Updated call with time.time()
        draw_blueprint_block(frame, px, py, GRID_SIZE, time.time())
    # =========================================================

    # ===== GRID (REVERTED TO STANDARD) =====
    for x in range(0, w, GRID_SIZE):
        cv2.line(frame, (x, 0), (x, h), (50, 50, 50), 1)
    for y in range(0, h, GRID_SIZE):
        cv2.line(frame, (0, y), (w, y), (50, 50, 50), 1)

    # ===== STRUCTURES (REVERTED TO SIMPLE + ACTIVE OUTLINE) =====
    active_idx = get_active_index()
    for i,s in enumerate(structures):
        size=int(GRID_SIZE*structure_scales[i])
        for level in range(structure_heights[i]):
            yoff=-level*(GRID_SIZE//2)
            for x,y in s:
                px=x*GRID_SIZE+(GRID_SIZE-size)//2
                py=y*GRID_SIZE+(GRID_SIZE-size)//2+yoff
                
                # Simple solid cyan block
                cv2.rectangle(frame, (px, py), (px + size, py + size), (255, 220, 0), -1)
                cv2.rectangle(frame, (px, py), (px + size, py + size), (255, 255, 0), 1)

                # Active structure outline (Step 2)
                if i == active_idx:
                    cv2.rectangle(
                        frame,
                        (px-2, py-2),
                        (px+size+2, py+size+2),
                        ACTIVE_OUTLINE_COLOR,
                        2
                    )

    # ===== MENU DRAW =====
    for i, m in enumerate(MODES):
        y = MENU_Y + i * MENU_H

        # Base color
        col = (0, 255, 0) if m == mode else (120, 120, 120)

        # Hover highlight
        if hovered_index == i:
            col = MENU_HOVER_COLOR

        cv2.rectangle(frame, (MENU_X, y), (MENU_X + MENU_W, y + MENU_H), col, 2)
        cv2.putText(
            frame,
            m,
            (MENU_X + 10, y + 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            col,
            2
        )

    if two_hand_ready:
        cv2.putText(frame,"3D MODE READY",(SCREEN_W//2-200,80),
                    cv2.FONT_HERSHEY_SIMPLEX,1.4,(0,255,255),3)

    cv2.putText(frame,f"Mode: {mode}",(20,40),
                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
    
    # STEP 5: DISABLE SCALE VISUAL
    if mode == "SCALE":
        cv2.putText(frame,"SCALE -> UNDO / REDO",
            (SCREEN_W//2 - 160, SCREEN_H - 60),
            cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,255),2)

    # (REMOVED PHASE D.2-A, D.2-B, D.2-C, D.2-D LOGIC HERE)

    # STEP 4: ===== COMMIT FEEDBACK =====
    if commit_message:
        if time.time() - commit_time < COMMIT_DISPLAY_TIME:
            cv2.putText(
                frame,
                commit_message,
                (SCREEN_W // 2 - 80, SCREEN_H - 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 0),  # cyan
                3
            )
        else:
            commit_message = None

    cv2.imshow("AirBlocks",frame)
    
    # STEP 4: KEYBOARD DETECTION
    key = cv2.waitKey(1)
    # ESC
    if key == 27:
        break
    # CTRL + Z -> Undo
    if key == 26 and undo_stack:
        redo_stack.append(snapshot_scene())
        restore_scene(undo_stack.pop())
    # CTRL + Y -> Redo
    if key == 25 and redo_stack:
        undo_stack.append(snapshot_scene())
        restore_scene(redo_stack.pop())

cap.release()
cv2.destroyAllWindows()