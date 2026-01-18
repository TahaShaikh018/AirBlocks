"""
colors.py
-----------
Centralized color definitions for AirBlocks.

Used by:
- Phase 6.x Editor (2D OpenCV rendering)
- Phase 7.x Viewer (OpenGL rendering)

All colors are in RGB format (0–255).
"""

# ================== BACKGROUND ==================

BACKGROUND = (30, 30, 30)
GRID = (60, 60, 60)

# ================== CURSOR & UI ==================

CURSOR = (255, 255, 0)          # Yellow
TEXT = (255, 255, 255)          # White
HIGHLIGHT = (0, 255, 255)       # Cyan

# ================== STRUCTURES ==================

STRUCTURE_DEFAULT = (0, 200, 0)     # Green
STRUCTURE_ACTIVE = (0, 100, 255)    # Blue
STRUCTURE_HOVER = (255, 180, 0)     # Orange

# ================== MENU ==================

MENU_IDLE = (140, 140, 140)     # Grey
MENU_SELECTED = (0, 255, 0)     # Green
MENU_TEXT = (255, 255, 255)     # White

# ================== 3D VIEWER ==================

VOXEL_DEFAULT = (0.2, 0.8, 0.2)      # Normalized for OpenGL
VOXEL_ACTIVE = (0.2, 0.4, 1.0)
VOXEL_GRID = (0.15, 0.15, 0.15)

# ================== DEBUG ==================

DEBUG = (255, 0, 0)             # Red
