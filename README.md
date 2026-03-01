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

## How to Use (Desktop Version)

1. Stand back so your full body (or at least your head, shoulders, and arms) is visible to the webcam.
2. Perform jumping jacks:
   - **Up Stage**: Raise your arms above your shoulders.
   - **Down Stage**: Lower your arms below your shoulders.
3. The counter will increment each time you complete a full repetition (Down -> Up -> Down).
4. If you stop for more than 7 seconds, the counter will reset to 0.
5. Press **'q'** while the video window is focused to exit the application.

**Note**: If the application is unresponsive, you can stop it from the terminal using **Ctrl+C**.

## Web Version

The application is also available as a web-based version that runs in your browser.

### Installation for Web Version

1. Make sure you have completed the basic installation steps above.

2. Install the additional web dependencies:

```bash
pip install flask
```

Or install all dependencies from requirements.txt:

```bash
pip install -r requirements.txt
```

### How to Run the Web Version

1. Make sure your virtual environment is activated.

2. Run the Flask web application:

```bash
python web_app.py
```

Or using the virtual environment's Python directly:

```bash
.venv/bin/python web_app.py  # On macOS/Linux
.venv\Scripts\python web_app.py  # On Windows
```

3. Open your web browser and navigate to:

```
http://127.0.0.1:5000
```

4. Allow browser access to your webcam when prompted.

5. The web interface will display:
   - Live video feed with pose detection
   - Real-time rep counter and stage indicator
   - Countdown timer for inactivity reset
   - Milestone markers at 50 and 100 reps
   - Reset button to manually reset the counter

6. To stop the web server, press **Ctrl+C** in the terminal.

### Features of Web Version

- **Browser-based**: No need to install OpenCV display dependencies
- **Modern UI**: Clean, responsive interface with gradient styling
- **Remote access**: Can be accessed from other devices on your local network
- **Manual reset**: Reset button for quick counter resets
- **Same detection**: Uses identical pose detection logic as desktop version
