import cv2
import mediapipe as mp
import time
import numpy as np

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

def calculate_angle(a, b, c):
    a = np.array(a) # First
    b = np.array(b) # Mid
    c = np.array(c) # End
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360 - angle
        
    return angle 

def main():
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Counter variables
    counter = 0
    stage = "down" # "up" or "down"
    
    # Inactivity reset variables
    last_activity_time = time.time()
    reset_delay = 7 # seconds
    
    # Signaling variables
    signal_50 = False
    signal_100 = False

    # Exit flag for button click
    exit_app = False

    def on_mouse_click(event, x, y, flags, param):
        nonlocal exit_app
        if event == cv2.EVENT_LBUTTONDOWN:
            # Check if click is within the terminate button area
            # Button now placed vertically on the left side below the counter
            if 0 <= x <= 200 and 450 <= y <= 530:
                exit_app = True

    cv2.namedWindow('Jumping Jack Counter', cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty('Jumping Jack Counter', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('Jumping Jack Counter', on_mouse_click)

    while cap.isOpened():
        if exit_app:
            break
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
            # 1. Arms: Shoulder (11, 12) and Wrist (15, 16)
            # 2. Legs: Hip (23, 24) and Ankle (27, 28)
            
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
            
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

            # Simplified logic for jumping jack:
            # - Arms are UP if wrists are above shoulders
            # - Arms are DOWN if wrists are below shoulders
            
            arms_up = left_wrist[1] < left_shoulder[1] and right_wrist[1] < right_shoulder[1]
            
            if arms_up and stage == "down":
                stage = "up"
                # Activity detected
                last_activity_time = current_time
            if not arms_up and stage == "up":
                stage = "down"
                counter += 1
                last_activity_time = current_time
                print(f"Jumping Jack Count: {counter}")
                
            # Signal check
            if counter == 50 and not signal_50:
                print("SIGNAL: 50 Jumping Jacks reached!")
                signal_50 = True
            if counter == 100 and not signal_100:
                print("SIGNAL: 100 Jumping Jacks reached!")
                signal_100 = True
                
        except Exception as e:
            pass

        # Check for inactivity reset
        time_since_last_activity = current_time - last_activity_time
        if time_since_last_activity > reset_delay:
            if counter > 0:
                print("Counter reset due to inactivity")
                counter = 0
                signal_50 = False
                signal_100 = False
            last_activity_time = current_time # Reset the timer to avoid continuous prints

        # Render counter - Vertical layout on left side
        # Setup status box - Narrow vertical box on left
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

        # Terminate Button - Below the counter box on left side
        cv2.rectangle(image, (0, 450), (200, 530), (0, 0, 255), -1)
        cv2.putText(image, 'EXIT', (50, 495),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)

        # Draw landmarks
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                 mp_drawing.DrawingSpec(color=(245,117,66), thickness=2, circle_radius=2), 
                                 mp_drawing.DrawingSpec(color=(245,66,230), thickness=2, circle_radius=2) 
                                 )               
        
        cv2.imshow('Jumping Jack Counter', image)

        # Handle keyboard exit (q or Esc)
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
