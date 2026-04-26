# AGENTS.md

This file provides guidance to coding agents working in this repository.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

Primary interface:

```bash
python web_app.py
```

The Flask app serves the site at `http://127.0.0.1:5000`.

Desktop/OpenCV version:

```bash
python jumping_jack_counter.py
```

Alternative entrypoint:

```bash
python main.py
```

## Test

Database/API smoke test:

```bash
python test_api.py
```

Manual API checks:

```bash
curl http://127.0.0.1:5000/api/sessions
curl -X POST http://127.0.0.1:5000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"total_reps": 100, "rounds": [{"round_index": 1, "reps": 50}, {"round_index": 2, "reps": 50}]}'
```

## Architecture

This repository contains two implementations of the same jumping-jack counter:

- `jumping_jack_counter.py`: desktop version using OpenCV windows.
- `web_app.py`: Flask server that streams webcam frames to the browser via MJPEG.

Both versions use MediaPipe Pose to detect landmarks. A rep is counted when the user transitions from arms-up back to arms-down. Inactivity triggers an automatic reset after 7 seconds.

In `web_app.py`, counter state is stored in module-level globals and mutated by the frame generator and reset/API routes. This assumes a single-process Flask runtime and does not isolate state across browser tabs.

## Data Model

SQLite database: `workouts.db`

- `sessions`: one row per workout session with aggregate counts.
- `rounds`: one row per round within a workout session.

A "round" is the period between resets. Recording a session persists the current round history and clears the in-memory round state.

## Templates

- `templates/index.html`: main camera counter UI
- `templates/history.html`: workout history UI
- `templates/reps_counter.html`: manual reps/rounds counter

## Working Notes

- Prefer the Flask web app unless the user explicitly asks for the desktop version.
- Be careful with shared mutable globals in `web_app.py`; changes can affect all connected clients.
- Keep the desktop and web counting logic aligned if modifying detection behavior.
