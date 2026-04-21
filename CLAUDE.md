# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Setup:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Run the web app (primary interface):**
```bash
python web_app.py
# Opens at http://127.0.0.1:5000
```

**Run the desktop (OpenCV window) version:**
```bash
python jumping_jack_counter.py
# or
python main.py
```

**Test database operations:**
```bash
python test_api.py
```

**Test API endpoints manually:**
```bash
curl http://127.0.0.1:5000/api/sessions
curl -X POST http://127.0.0.1:5000/api/sessions \
     -H "Content-Type: application/json" \
     -d '{"total_reps": 100, "rounds": [{"round_index": 1, "reps": 50}, {"round_index": 2, "reps": 50}]}'
```

## Architecture

This is a Flask web application with two parallel implementations of the same jumping jack counter logic:

- **`jumping_jack_counter.py`** — standalone desktop version using `cv2.imshow`. Runs fullscreen with a click-to-exit button.
- **`web_app.py`** — Flask server that exposes the webcam feed as a multipart JPEG stream via `/video_feed`. The detection loop runs in a generator function (`generate_frames`) on the server; the browser renders it in an `<img>` tag via MJPEG streaming.

Both share identical pose detection logic: MediaPipe Pose estimates body landmarks, and "arms up" is detected when both wrists' Y-coordinates are above (numerically less than) both shoulders' Y-coordinates in normalized image space. A rep increments when the state transitions from "up" back to "down". The counter auto-resets after 7 seconds of inactivity.

**State management in `web_app.py`:** Counter state (`counter`, `stage`, `round_history`, etc.) lives in module-level globals, mutated by `generate_frames()` and the `/reset` endpoint. This works because Flask runs in a single process (`threaded=True`). There is no session isolation between browser tabs.

**Database (`workouts.db` — SQLite):**
- `sessions`: one row per recorded workout (`trained_at`, `total_jumps`, `round_count`)
- `rounds`: one row per round within a session (`session_id FK`, `round_index`, `jumps`, `ended_at`)

A "round" is the period between resets. The `/reset` endpoint appends the current count to `round_history`. `/api/record_session` (POST) persists `round_history` to the DB and clears it. There is also a legacy `/api/sessions` POST endpoint that accepts round data directly from the client.

**Templates (`templates/`):**
- `index.html` — main jumping jack counter page (MJPEG feed + `/api/counter` polling)
- `history.html` — workout history page (fetches `/api/sessions`)
- `reps_counter.html` — manual reps & rounds counter (no camera, pure JS)
