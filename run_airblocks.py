import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

editor_path = os.path.join(BASE_DIR, "phase6_1_final_selection.py")
viewer_path = os.path.join(BASE_DIR, "phase7_viewer", "viewer_3d.py")

print(" Launching AirBlocks...")
print(" Starting Gesture Editor")
print(" Starting 3D Viewer")

# Start editor
subprocess.Popen([sys.executable, editor_path])

# Start viewer
subprocess.Popen([sys.executable, viewer_path])

print(" AirBlocks is running")
