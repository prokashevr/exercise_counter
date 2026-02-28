# Jumping Jack Counter

This application uses computer vision to count jumping jacks in real-time using your webcam. It helps reduce cognitive load during exercise by tracking your repetitions and providing automatic reset functionality.

## Features

- **Real-time Counting**: Automatically counts jumping jacks using MediaPipe Pose estimation.
- **Inactivity Reset**: The counter resets to zero after 7 seconds of inactivity (no movement detected).
- **Progress Signals**: Displays visual markers when you reach 50 and 100 repetitions.
- **Live Overlay**: Shows your current rep count, exercise stage (up/down), and the countdown to inactivity reset directly on the video feed.

## Prerequisites

- Python 3.8 or higher
- A working webcam

## Installation

1. Clone or download this repository.
2. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install opencv-python mediapipe numpy
```

## How to Run

Make sure your virtual environment is activated, then run:

```bash
python jumping_jack_counter.py
```

**Important**: Always use the virtual environment's Python directly. If you get `ModuleNotFoundError: No module named 'cv2'`, make sure you're using the correct Python:

```bash
# Use the virtual environment's Python directly
.venv/bin/python jumping_jack_counter.py  # On macOS/Linux
.venv\Scripts\python jumping_jack_counter.py  # On Windows
```

## How to Use

1. Stand back so your full body (or at least your head, shoulders, and arms) is visible to the webcam.
2. Perform jumping jacks:
   - **Up Stage**: Raise your arms above your shoulders.
   - **Down Stage**: Lower your arms below your shoulders.
3. The counter will increment each time you complete a full repetition (Down -> Up -> Down).
4. If you stop for more than 7 seconds, the counter will reset to 0.
5. Press **'q'** while the video window is focused to exit the application.
