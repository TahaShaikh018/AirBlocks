"""
cube_renderer.py
----------------
Low-level OpenGL cube (voxel) rendering utilities.

Used by:
- phase7_viewer/viewer_3d.py

This module draws cubes only.
"""

from OpenGL.GL import *


# ================== CUBE GEOMETRY ==================

# Cube vertices (unit cube centered at origin)
CUBE_VERTICES = [
    (-0.5, -0.5, -0.5),
    ( 0.5, -0.5, -0.5),
    ( 0.5,  0.5, -0.5),
    (-0.5,  0.5, -0.5),
    (-0.5, -0.5,  0.5),
    ( 0.5, -0.5,  0.5),
    ( 0.5,  0.5,  0.5),
    (-0.5,  0.5,  0.5),
]

# Cube faces (indices into vertices)
CUBE_FACES = [
    (0, 1, 2, 3),  # back
    (4, 5, 6, 7),  # front
    (0, 4, 7, 3),  # left
    (1, 5, 6, 2),  # right
    (3, 2, 6, 7),  # top
    (0, 1, 5, 4),  # bottom
]

# Normals for lighting
CUBE_NORMALS = [
    (0, 0, -1),
    (0, 0,  1),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 1, 0),
    (0, -1, 0),
]


# ================== DRAW FUNCTION ==================

def draw_cube(position, size=1.0, color=(1.0, 1.0, 1.0)):
    """
    Draw a cube at a given position.

    :param position: (x, y, z)
    :param size: cube size
    :param color: (r, g, b) normalized (0–1) or None
    """
    x, y, z = position

    glPushMatrix()
    glTranslatef(x, y, z)
    glScalef(size, size, size)
    
    # MODIFIED: Check for None to support wireframe rendering (which handles its own color)
    if color is not None:
        glColor3f(*color)

    glBegin(GL_QUADS)
    for face, normal in zip(CUBE_FACES, CUBE_NORMALS):
        glNormal3f(*normal)
        for vertex_index in face:
            glVertex3f(*CUBE_VERTICES[vertex_index])
    glEnd()

    glPopMatrix()