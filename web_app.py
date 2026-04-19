from flask import Flask, render_template, Response, request, jsonify
import cv2
import mediapipe as mp
import time
import numpy as np
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Database configuration
DB_NAME = 'workouts.db'

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Global variables for counter state
counter = 0
stage = "down"
last_activity_time = time.time()
reset_delay = 7
signal_50 = False
signal_100 = False
round_history = []  # Track jumps per round

def init_database():
    """Initialize the database and create tables if they don't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Create sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trained_at TEXT NOT NULL,
            total_jumps INTEGER NOT NULL,
            round_count INTEGER NOT NULL
        )
    ''')

    # Create rounds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            round_index INTEGER NOT NULL,
            jumps INTEGER NOT NULL,
            ended_at TEXT NOT NULL,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    ''')

    conn.commit()
    conn.close()

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle

def generate_frames():
    global counter, stage, last_activity_time, signal_50, signal_100

    cap = cv2.VideoCapture(0)
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Recolor image to RGB
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False

        # Make detection
        results = pose.process(image)

        # Recolor back to BGR
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        current_time = time.time()

        try:
            landmarks = results.pose_landmarks.landmark

            # Get coordinates for jumping jack detection
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                           landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,
                            landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]

            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x,
                          landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Arms are UP if wrists are above shoulders
            arms_up = left_wrist[1] < left_shoulder[1] and right_wrist[1] < right_shoulder[1]

            if arms_up and stage == "down":
                stage = "up"
                last_activity_time = current_time
            if not arms_up and stage == "up":
                stage = "down"
                counter += 1
                last_activity_time = current_time

            # Signal check
            if counter == 50 and not signal_50:
                signal_50 = True
            if counter == 100 and not signal_100:
                signal_100 = True

        except Exception as e:
            pass

        # Check for inactivity reset
        time_since_last_activity = current_time - last_activity_time
        if time_since_last_activity > reset_delay:
            if counter > 0:
                counter = 0
                signal_50 = False
                signal_100 = False
            last_activity_time = current_time

        # Render counter - Vertical layout on left side
        cv2.rectangle(image, (0,0), (200, 440), (245, 117, 16), -1)

        # Rep data
        cv2.putText(image, 'REPS', (15,40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(image, str(counter),
                    (20,140),
                    cv2.FONT_HERSHEY_SIMPLEX, 4, (255,255,255), 5, cv2.LINE_AA)

        # Stage data
        cv2.putText(image, 'STAGE', (15,200),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,0), 2, cv2.LINE_AA)
        cv2.putText(image, stage,
                    (20,270),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 3, cv2.LINE_AA)

        # Reset timer
        if counter > 0:
            remaining = max(0, reset_delay - time_since_last_activity)
            cv2.putText(image, f'{remaining:.1f}s', (30, 320),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)

        # Signal markers
        if counter >= 50:
            cv2.putText(image, '50!', (50, 360),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)
        if counter >= 100:
            cv2.putText(image, '100!', (40, 400),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3, cv2.LINE_AA)

        # Draw landmarks
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                 mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2),
                                 mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2))

        # Encode frame
        ret, buffer = cv2.imencode('.jpg', image)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    pose.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/reps-counter')
def reps_counter():
    return render_template('reps_counter.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/counter')
def get_counter():
    """Get current counter value for frontend tracking."""
    global counter
    return jsonify({'counter': counter})

@app.route('/reset')
def reset():
    global counter, stage, signal_50, signal_100, last_activity_time, round_history

    # Save current counter to round history before resetting
    if counter > 0:
        round_history.append(counter)

    counter = 0
    stage = "down"
    signal_50 = False
    signal_100 = False
    last_activity_time = time.time()

    # Return updated session info
    total_jumps = sum(round_history)
    return {
        'status': 'reset',
        'counter': counter,
        'round_count': len(round_history),
        'total_jumps': total_jumps
    }

@app.route('/api/current_session')
def get_current_session():
    """Get current session data (for recording)."""
    global counter, round_history

    # Include current counter if it's > 0
    rounds = round_history.copy()
    if counter > 0:
        rounds.append(counter)

    total_jumps = sum(rounds)

    return jsonify({
        'counter': counter,
        'rounds': rounds,
        'total_jumps': total_jumps,
        'round_count': len(rounds)
    })

@app.route('/api/record_session', methods=['POST'])
def record_session():
    """Record current session to database and clear round history."""
    global counter, round_history

    # Include current counter if it's > 0
    rounds = round_history.copy()
    if counter > 0:
        rounds.append(counter)

    if not rounds:
        return jsonify({'ok': False, 'error': 'No workout data to record'}), 400

    total_jumps = sum(rounds)
    trained_at = datetime.now().isoformat()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO sessions (trained_at, total_jumps, round_count)
            VALUES (?, ?, ?)
        ''', (trained_at, total_jumps, len(rounds)))

        session_id = cursor.lastrowid

        for index, jumps in enumerate(rounds, start=1):
            cursor.execute('''
                INSERT INTO rounds (session_id, round_index, jumps)
                VALUES (?, ?, ?)
            ''', (session_id, index, jumps))

        conn.commit()
        conn.close()

        # Clear round history after successful save
        round_history = []

        return jsonify({'ok': True, 'session_id': session_id, 'total_jumps': total_jumps})

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/sessions', methods=['POST'])
def save_session():
    """Save a completed workout session to the database with rounds."""
    try:
        data = request.get_json()

        # Validate required fields
        if 'total_reps' not in data or 'rounds' not in data:
            return jsonify({'ok': False, 'error': 'Missing required fields'}), 400

        total_reps = data['total_reps']
        rounds = data['rounds']

        # Validate rounds format
        if not isinstance(rounds, list) or len(rounds) == 0:
            return jsonify({'ok': False, 'error': 'Invalid rounds data'}), 400

        # Use provided trained_at or current datetime
        trained_at = data.get('trained_at', datetime.now().isoformat())

        # Calculate round count
        round_count = len(rounds)

        # Open database connection
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        # Insert session
        cursor.execute('''
            INSERT INTO sessions (trained_at, total_jumps, round_count)
            VALUES (?, ?, ?)
        ''', (trained_at, total_reps, round_count))

        # Get last inserted session id
        session_id = cursor.lastrowid

        # Insert all rounds
        for round_data in rounds:
            round_index = round_data.get('round_index')
            reps = round_data.get('reps')
            ended_at = round_data.get('ended_at', datetime.now().isoformat())

            cursor.execute('''
                INSERT INTO rounds (session_id, round_index, jumps, ended_at)
                VALUES (?, ?, ?, ?)
            ''', (session_id, round_index, reps, ended_at))

        # Commit transaction
        conn.commit()
        conn.close()

        return jsonify({'ok': True, 'session_id': session_id})

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Retrieve all workout sessions ordered by trained_at DESC."""
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all sessions ordered by trained_at DESC
        cursor.execute('''
            SELECT id, trained_at, total_jumps, round_count
            FROM sessions
            ORDER BY trained_at DESC
        ''')
        sessions = cursor.fetchall()

        # Build result with rounds for each session
        result = []
        for session in sessions:
            session_dict = {
                'id': session['id'],
                'trained_at': session['trained_at'],
                'total_jumps': session['total_jumps'],
                'round_count': session['round_count'],
                'rounds': []
            }

            # Get rounds for this session
            cursor.execute('''
                SELECT round_index, jumps, ended_at
                FROM rounds
                WHERE session_id = ?
                ORDER BY round_index ASC
            ''', (session['id'],))
            rounds = cursor.fetchall()

            session_dict['rounds'] = [
                {'round_index': r['round_index'], 'jumps': r['jumps'], 'ended_at': r['ended_at']}
                for r in rounds
            ]

            result.append(session_dict)

        conn.close()

        return jsonify({'ok': True, 'sessions': result})

    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500

if __name__ == '__main__':
    init_database()
    app.run(debug=True, threaded=True)
