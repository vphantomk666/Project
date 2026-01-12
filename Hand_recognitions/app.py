import cv2
import mediapipe as mp
import os
import keyboard
import time

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)

def finger_is_up(lm, tip_id, pip_id):
    return lm[tip_id].y < lm[pip_id].y

# Flags to avoid repeating app launches
thumbs_up_triggered = False
peace_triggered = False
fist_triggered = False
open_palm_triggered = False

gesture_control_enabled = True
last_toggle_time = 0  # For debounce

while cap.isOpened():
    success, image = cap.read()
    if not success:
        break

    # === Toggle control on F8 key press ===
    if keyboard.is_pressed('ctrl + f1'):
        current_time = time.time()
        if current_time - last_toggle_time > 1:  # debounce 1 second
            gesture_control_enabled = not gesture_control_enabled
            state = "ENABLED ✅" if gesture_control_enabled else "DISABLED ❌"
            print(f"[TOGGLE] Gesture control {state}")
            last_toggle_time = current_time

    image = cv2.flip(image, 1)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = hands.process(image_rgb)

    if gesture_control_enabled and result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark

            thumb_up = lm[4].y < lm[3].y
            index_up = finger_is_up(lm, 8, 6)
            middle_up = finger_is_up(lm, 12, 10)
            ring_up = finger_is_up(lm, 16, 14)
            pinky_up = finger_is_up(lm, 20, 18)

            fingers = [thumb_up, index_up, middle_up, ring_up, pinky_up]
            total_fingers_up = sum(fingers)

            gesture = None
            action = None

            if thumb_up and not any([index_up, middle_up, ring_up, pinky_up]):
                gesture = "Thumbs Up 👍"
                action = "Opening Notepad"
                if not thumbs_up_triggered:
                    print("👍 Opening Notepad...")
                    os.system("start notepad")
                    thumbs_up_triggered = True

            elif index_up and middle_up and not (ring_up or pinky_up or thumb_up):
                gesture = "Peace ✌️"
                action = "Opening YouTube"
                if not peace_triggered:
                    print("✌️ Opening YouTube...")
                    os.system("start chrome https://www.youtube.com")
                    peace_triggered = True

            elif total_fingers_up == 0:
                gesture = "Fist ✊"
                action = "Opening Paint"
                if not fist_triggered:
                    print("✊ Opening Paint...")
                    os.system("start mspaint")
                    fist_triggered = True

            elif total_fingers_up == 5:
                gesture = "Open Palm 🖐️"
                action = "Opening Chrome"
                if not open_palm_triggered:
                    print("🖐️ Opening Chrome...")
                    os.system("start chrome")
                    open_palm_triggered = True

            else:
                # Reset flags if no recognized gesture
                thumbs_up_triggered = False
                peace_triggered = False
                fist_triggered = False
                open_palm_triggered = False

            if gesture:
                cv2.putText(image, gesture, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(image, action, (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    elif not gesture_control_enabled:
        cv2.putText(image, "Gesture Control DISABLED ❌ (Press F8)", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Hand Gesture Control", image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exit")
        break

cap.release()
cv2.destroyAllWindows()
