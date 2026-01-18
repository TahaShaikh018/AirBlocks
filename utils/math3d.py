"""
math3d.py
----------
Basic 3D math utilities for AirBlocks.

Used by:
- Phase 7.x OpenGL viewer
- Future phases (rotation, physics, AR)

No OpenGL or rendering code here.
"""

import math

# ================== BASIC HELPERS ==================

def clamp(value, min_value, max_value):
    """Clamp a value between min and max."""
    return max(min_value, min(max_value, value))


# ================== VECTOR OPERATIONS ==================

def vec3(x, y, z):
    """Create a 3D vector."""
    return [float(x), float(y), float(z)]


def add(v1, v2):
    """Add two vectors."""
    return [
        v1[0] + v2[0],
        v1[1] + v2[1],
        v1[2] + v2[2],
    ]


def sub(v1, v2):
    """Subtract v2 from v1."""
    return [
        v1[0] - v2[0],
        v1[1] - v2[1],
        v1[2] - v2[2],
    ]


def scale(v, s):
    """Scale vector by scalar."""
    return [
        v[0] * s,
        v[1] * s,
        v[2] * s,
    ]


def length(v):
    """Return vector length."""
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def normalize(v):
    """Normalize vector (safe)."""
    l = length(v)
    if l == 0:
        return [0.0, 0.0, 0.0]
    return [
        v[0] / l,
        v[1] / l,
        v[2] / l,
    ]


# ================== ROTATION HELPERS ==================

def rotate_y(v, angle_deg):
    """Rotate vector around Y-axis."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    x, y, z = v
    return [
        x * cos_a + z * sin_a,
        y,
        -x * sin_a + z * cos_a,
    ]


def rotate_x(v, angle_deg):
    """Rotate vector around X-axis."""
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    x, y, z = v
    return [
        x,
        y * cos_a - z * sin_a,
        y * sin_a + z * cos_a,
    ]
