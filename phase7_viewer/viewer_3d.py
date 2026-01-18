import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
from data.scene_data import load_scene, structures, structure_scales, structure_heights, get_active_index
from phase7_viewer.cube_renderer import draw_cube
from utils.colors import VOXEL_DEFAULT, VOXEL_ACTIVE, BACKGROUND

# ================== CAMERA STATE ==================
yaw = 0.0
pitch = 20.0
distance = 40.0

# STEP 1: Smooth camera targets
target_yaw = yaw
target_pitch = pitch
target_distance = distance

CAMERA_SMOOTH = 0.15

# CHANGE 2: Store focus target
focus_center = (0, 0, 0)

last_x = 0
last_y = 0
left_down = False
right_down = False

frame_count = 0

# ================== OPENGL INIT ==================
def init_gl():
    glEnable(GL_DEPTH_TEST)

    # STEP 1: Enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    # Light color (soft white)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.25, 0.25, 0.25, 1.0))

    # Light direction (top-left-front)
    glLightfv(GL_LIGHT0, GL_POSITION, (-1.0, 1.5, 1.0, 0.0))

    # Enable material coloring
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    # STEP 1 (NEW): Prevent z-fighting for wireframe overlay
    glEnable(GL_POLYGON_OFFSET_FILL)
    glPolygonOffset(1.0, 1.0)

    glClearColor(*(c / 255 for c in BACKGROUND), 1)

# CHANGE 1: Add helper to compute scene bounds
def compute_scene_bounds():
    if not structures:
        return (0, 0, 0), 10

    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")

    for i, s in enumerate(structures):
        for level in range(structure_heights[i]):
            for x, y in s:
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, level)
                max_y = max(max_y, level)
                min_z = min(min_z, y)
                max_z = max(max_z, y)

    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    cz = (min_z + max_z) / 2

    radius = max(
        max_x - min_x,
        max_y - min_y,
        max_z - min_z
    ) * 1.5 + 2

    return (cx, cy, cz), radius

# STEP 1: Add helper to compute stats
def compute_scene_stats():
    total_blocks = 0
    max_height = 0

    for i, s in enumerate(structures):
        total_blocks += len(s) * structure_heights[i]
        max_height = max(max_height, structure_heights[i])

    return {
        "structures": len(structures),
        "blocks": total_blocks,
        "active": get_active_index(),
        "height": max_height
    }

# STEP 2: Add a 2D HUD draw helper
def draw_stats_hud(stats):
    glDisable(GL_LIGHTING)

    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 700)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.7, 0.9, 1.0)  # cyan-white HUD

    lines = [
        f"Structures : {stats['structures']}",
        f"Total Blocks : {stats['blocks']}",
        f"Active ID : {stats['active']}",
        f"Max Height : {stats['height']}",
    ]

    y = 660
    for line in lines:
        glRasterPos2f(20, y)
        for ch in line:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))
        y -= 24

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_LIGHTING)

# ================== DISPLAY ==================
def display():
    # STEP 1: FIX display() FUNCTION HEADER
    global frame_count, focus_center, target_distance
    
    # STEP 3: Smooth camera every frame
    global yaw, pitch, distance
    yaw += (target_yaw - yaw) * CAMERA_SMOOTH
    pitch += (target_pitch - pitch) * CAMERA_SMOOTH
    distance += (target_distance - distance) * CAMERA_SMOOTH

    frame_count += 1

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # CHANGE 4: Apply focus in camera transform
    glTranslatef(0, 0, -distance)
    glRotatef(pitch, 1, 0, 0)
    glRotatef(yaw, 0, 1, 0)
    
    # Focus camera on structure center
    fx, fy, fz = focus_center
    glTranslatef(-fx, -fy, -fz)

    if frame_count % 10 == 0:
        load_scene()
        # CHANGE 3: Update focus automatically when scene reloads
        # STEP 2: REMOVED the later global line
        focus_center, target_distance = compute_scene_bounds()

    # STEP 1: Adjust colors at draw time (SOLID PASS)
    active = get_active_index()
    for i, s in enumerate(structures):

        if i == active:
            color = VOXEL_ACTIVE
            glColor3f(1.0, 1.0, 1.0)  # full brightness
        else:
            color = VOXEL_DEFAULT
            glColor3f(0.85, 0.85, 0.85)  # slightly darker

        for level in range(structure_heights[i]):
            for x, y in s:
                draw_cube((x, level, y), structure_scales[i], color)

    # STEP 3 (NEW): ===== WIREFRAME OVERLAY =====
    glDisable(GL_LIGHTING)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glLineWidth(1.5)

    glColor3f(0.7, 0.9, 1.0)  # futuristic cyan-white
    for i, s in enumerate(structures):
        for level in range(structure_heights[i]):
            for x, y in s:
                draw_cube((x, level, y), structure_scales[i], None)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glEnable(GL_LIGHTING)
    # ===========================================

    # STEP 3: Call HUD from display()
    stats = compute_scene_stats()
    draw_stats_hud(stats)

    glutSwapBuffers()

# ================== MOUSE CONTROLS ==================
def mouse(button, state, x, y):
    global left_down, right_down, last_x, last_y

    if button == GLUT_LEFT_BUTTON:
        left_down = (state == GLUT_DOWN)
    if button == GLUT_RIGHT_BUTTON:
        right_down = (state == GLUT_DOWN)

    last_x = x
    last_y = y

# STEP 2: Update mouse motion to affect TARGETS
def motion(x, y):
    global target_yaw, target_pitch, target_distance, last_x, last_y

    dx = x - last_x
    dy = y - last_y

    if left_down:
        target_yaw += dx * 0.5
        target_pitch += dy * 0.5
        target_pitch = max(-85, min(85, target_pitch))

    if right_down:
        target_distance += dy * 0.2
        # CHANGE 1: Lower minimum zoom distance
        target_distance = max(1.5, min(300, target_distance))

    last_x = x
    last_y = y

# STEP 4: Smooth mouse wheel zoom
def mouse_wheel(button, direction, x, y):
    global target_distance
    if direction > 0:
        target_distance -= 3
    else:
        target_distance += 3
    # CHANGE 1: Lower minimum zoom distance
    target_distance = max(1.5, min(300, target_distance))

# CHANGE 1: Add keyboard handler
def keyboard(key, x, y):
    global focus_center, target_distance

    if key in [b'f', b'F']:
        focus_center, target_distance = compute_scene_bounds()

# ================== WINDOW ==================
def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / max(h, 1), 0.1, 1000)
    glMatrixMode(GL_MODELVIEW)

def idle():
    glutPostRedisplay()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 700)
    glutCreateWindow(b"AirBlocks 3D Viewer (Mouse Control)")

    init_gl()

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutIdleFunc(idle)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutMouseWheelFunc(mouse_wheel)
    
    # CHANGE 2: Register keyboard callback
    glutKeyboardFunc(keyboard)

    glutMainLoop()

if __name__ == "__main__":
    main()