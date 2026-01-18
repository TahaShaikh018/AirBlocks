"""
camera.py
----------
Simple orbit-style camera for OpenGL 3D viewer.

Used by:
- phase7_viewer/viewer_3d.py

Controls:
- Mouse drag -> rotate
- Mouse scroll -> zoom
"""

from OpenGL.GL import *
from OpenGL.GLU import *
from utils.math3d import clamp


class Camera:
    def __init__(self):
        # Rotation angles
        self.rot_x = 25.0
        self.rot_y = -45.0

        # Distance from scene
        self.distance = 20.0

        # Mouse state
        self.last_mouse_x = None
        self.last_mouse_y = None
        self.dragging = False

        # Sensitivity
        self.rotate_speed = 0.4
        self.zoom_speed = 1.0

        # Limits
        self.min_distance = 5.0
        self.max_distance = 80.0

    # ================== CAMERA TRANSFORM ==================

    def apply(self):
        """
        Apply camera transformation.
        Call this BEFORE drawing the scene.
        """
        glTranslatef(0.0, 0.0, -self.distance)
        glRotatef(self.rot_x, 1.0, 0.0, 0.0)
        glRotatef(self.rot_y, 0.0, 1.0, 0.0)

    # ================== MOUSE EVENTS ==================

    def mouse_button(self, button, state, x, y):
        """
        Handle mouse button events.
        """
        if button == 0:  # Left mouse button
            if state == 0:  # Press
                self.dragging = True
                self.last_mouse_x = x
                self.last_mouse_y = y
            else:  # Release
                self.dragging = False

        # Mouse wheel (GLUT style)
        if button == 3:  # Scroll up
            self.distance -= self.zoom_speed
        elif button == 4:  # Scroll down
            self.distance += self.zoom_speed

        self.distance = clamp(self.distance,
                               self.min_distance,
                               self.max_distance)

    def mouse_motion(self, x, y):
        """
        Handle mouse drag motion.
        """
        if not self.dragging:
            return

        dx = x - self.last_mouse_x
        dy = y - self.last_mouse_y

        self.rot_y += dx * self.rotate_speed
        self.rot_x += dy * self.rotate_speed

        # Prevent flipping
        self.rot_x = clamp(self.rot_x, -89.0, 89.0)

        self.last_mouse_x = x
        self.last_mouse_y = y
