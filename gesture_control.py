import cv2
import mediapipe as mp
import numpy as np
import joblib
import socket
import os
import time
import math

# === TCP Setup ===
HOST = "127.0.0.1"   # MATLAB running locally
PORT = 55001         # must match MATLAB TCP server port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print("🔌 Connecting to MATLAB TCP server...")
while True:
    try:
        sock.connect((HOST, PORT))
        print("✅ Connected to MATLAB TCP server.")
        break
    except ConnectionRefusedError:
        print("⏳ Waiting for MATLAB server... (run your MATLAB TCP script first)")
        time.sleep(2)

# === Load trained model ===
model_path = os.path.join(os.path.expanduser("~"), "OneDrive", "Desktop", "gesture_model.pkl")
model = joblib.load(model_path)

# === Setup MediaPipe Hands ===
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7,
                       min_tracking_confidence=0.7)

# === Helper: compute continuous direction angle (0–360°) ===
def detect_angle(landmarks, w, h):
    base_id = 9   # base of middle finger
    tip_id = 12   # tip of middle finger
    x0, y0 = landmarks[base_id].x * w, landmarks[base_id].y * h
    x1, y1 = landmarks[tip_id].x * w, landmarks[tip_id].y * h
    dx, dy = x1 - x0, y1 - y0
    angle = (math.degrees(math.atan2(-dy, dx)) + 360) % 360
    return angle

# === Start webcam ===
cap = cv2.VideoCapture(0)
print("🎥 Gesture + angle control started — press 'q' to quit.\n")

last_gesture = None
last_send_time = 0
send_delay = 0.25  # seconds between angle updates
angle_smooth = None
mode = "STOP"  # current movement mode

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    h, w, _ = frame.shape
    gesture = "No Hand"
    angle = None

    if results.multi_hand_landmarks:
        lm = results.multi_hand_landmarks[0].landmark
        row = np.array([[p.x, p.y, p.z] for p in lm]).flatten().reshape(1, -1)
        gesture_pred = model.predict(row)
        gesture = gesture_pred[0]
        mp_drawing.draw_landmarks(frame, results.multi_hand_landmarks[0],
                                  mp_hands.HAND_CONNECTIONS)

        # Compute angle of hand orientation
        angle = detect_angle(lm, w, h)
        if angle_smooth is None:
            angle_smooth = angle
        else:
            angle_smooth = 0.7 * angle_smooth + 0.3 * angle

        # === Handle commands ===
        if gesture != last_gesture:
            if gesture == "FIST":
                mode = "STOP"
                msg = "STOP\n"
                sock.sendall(msg.encode())
                print("🔴 FIST detected → STOP")
            elif gesture == "OPEN":
                mode = "START"
                print("🟢 OPEN detected → START (continuous angle mode)")
            last_gesture = gesture

        # === If in START mode, continuously send angle ===
        if mode == "START":
            if (time.time() - last_send_time) > send_delay:
                msg = f"{angle_smooth:.2f}\n"
                sock.sendall(msg.encode())
                print(f"[SEND] Angle: {angle_smooth:.2f}°")
                last_send_time = time.time()

    # === Display on video ===
    display_text = f"Gesture: {gesture}"
    if angle_smooth is not None:
        display_text += f" | Angle: {int(angle_smooth)}°"
    cv2.putText(frame, display_text, (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

    cv2.imshow("Gesture + 360° Control (TCP → MATLAB)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
hands.close()
sock.close()
print("👋 Disconnected and closed.")



