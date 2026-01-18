# AirBlocks
## Gesture-Based 3D Spatial Construction System

Design in the air. Build in space.

---

## Introduction

AirBlocks is a gesture-driven 3D construction system that allows users to design,
manipulate, and visualize block-based structures using natural hand gestures.
It combines computer vision, interaction design, and 3D graphics to explore
next-generation Human–Computer Interaction (HCI).

---

## Key Features

- Gesture-based building using pinch, fist, and vertical motion
- Explicit structure selection (GROUP mode)
- Extrusion-based height control
- Undo / Redo support
- Dedicated 3D OpenGL viewer
- Smooth camera controls with auto-fit and refocus
- CAD-style wireframe overlay
- Live scene statistics HUD

---

## System Architecture

Camera Input
    -> Gesture Editor (OpenCV + MediaPipe)
    -> Scene Export (JSON)
    -> 3D Viewer (OpenGL)

The editor is responsible only for interaction and construction.
The viewer is responsible only for visualization.
Both communicate through a shared scene file.

---

## Technology Stack

Editor:
- Python
- OpenCV
- MediaPipe Hands
- CustomTkinter

Viewer:
- PyOpenGL
- GLUT
- Fixed-pipeline OpenGL

Data:
- JSON-based scene persistence

---

## Project Structure

AirBlocks/
|
|-- phase6_1_final_selection.py   # Gesture-based editor
|-- run_airblocks.py              # Unified launcher
|-- data/
|   |-- scene_data.py
|   |-- scene_snapshot.json
|
|-- phase7_viewer/
|   |-- viewer_3d.py
|   |-- cube_renderer.py
|
|-- utils/
|   |-- colors.py
|
|-- requirements.txt
|-- README.md

---

## Installation

Install all dependencies using:

pip install -r requirements.txt

---

## Running AirBlocks

Use the unified launcher:

python run_airblocks.py

This will start:
- The gesture-based editor
- The 3D OpenGL viewer

Both components run together and stay synchronized.

---

## Controls

Editor:
- Pinch + hold: Build structure
- Pinch (GROUP mode): Select structure
- Fist: Move selected structure
- Pinch + up/down (EXTRUDE): Change height
- CTRL + Z / CTRL + Y: Undo / Redo

Viewer:
- Left mouse drag: Rotate camera
- Right mouse drag / scroll: Zoom
- F key: Re-focus camera
- HUD: Live scene statistics

---

## AI Integration (Planned)

Future versions of AirBlocks will include an AI text assistant that converts
natural language instructions into structured build commands, while keeping
gesture interaction as the primary control method.

---

## Future Scope

- AI-assisted natural language building
- Web-based version using Three.js and MediaPipe JS
- AR / VR adaptation
- Collaborative multi-user editing
- Export to standard 3D formats

---

## Author

Taha Shaikh
B.Tech - Artificial Intelligence & Data Science

---

## License

Developed for academic and educational purposes.
