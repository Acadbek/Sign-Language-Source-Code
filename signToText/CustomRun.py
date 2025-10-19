import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import time
import mediapipe as mp
from tensorflow.keras.models import load_model

mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils


def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = model.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    return image, results


def draw_styled_landmarks(image, results):
    # Draw face connections
    mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
                              mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1)
                              )
    # Draw pose connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2)
                              )
    # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2)
                              )
    # Draw right hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2)
                              )


def extract_keypoints(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
                     results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
    face = np.array([[res.x, res.y, res.z] for res in
                     results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
    lh = np.array([[res.x, res.y, res.z] for res in
                   results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
    rh = np.array([[res.x, res.y, res.z] for res in
                   results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
        21 * 3)
    return np.concatenate([pose, face, lh, rh])


def has_hand(results):
    """Check if at least one hand is detected"""
    return results.left_hand_landmarks is not None or results.right_hand_landmarks is not None


def prob_viz(res, actions, input_frame, colors):
    """Visualize prediction probabilities as bars"""
    output_frame = input_frame.copy()

    # Safety check
    if len(res) != len(actions) or len(res) != len(colors):
        print(f"Warning: Mismatch in prob_viz - res:{len(res)}, actions:{len(actions)}, colors:{len(colors)}")
        return output_frame

    for num, prob in enumerate(res):
        # Draw probability bar
        cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), colors[num], -1)
        # Draw action name
        cv2.putText(output_frame, actions[num], (0, 85 + num * 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,
                    cv2.LINE_AA)

    return output_frame


# Load model first to determine the number of actions
try:
    model = load_model('actions_holistic.keras')
    print("Model loaded successfully!")
except:
    print("Error: Could not load model 'actions_holistic.keras'")
    print("Please train the model first using CustomNeuralNetwork.py")
    exit()

# Get number of actions from model output shape
num_actions = model.output_shape[-1]
print(f"Model trained on {num_actions} actions")

# Load action names from saved file
actions_file = 'actions_holistic_actions.npy'
if os.path.exists(actions_file):
    actions = np.load(actions_file)
    print(f"Loaded actions: {actions}")
else:
    print(f"⚠️  Warning: {actions_file} not found!")
    print("Trying to load from MP_Data folder...")
    DATA_PATH = os.path.join('MP_Data')
    if os.path.exists(DATA_PATH):
        actions = np.array(sorted([folder for folder in os.listdir(DATA_PATH)
                                   if os.path.isdir(os.path.join(DATA_PATH, folder))]))
        print(f"Loaded actions from MP_Data: {actions}")
    else:
        print("❌ ERROR: Cannot find action names!")
        exit()

# Verify actions match model
if len(actions) != num_actions:
    print(f"⚠️  WARNING: Mismatch detected!")
    print(f"   Model expects {num_actions} actions but found {len(actions)} action names")
    print(f"   Using only first {num_actions} actions from: {actions}")
    actions = actions[:num_actions]

# Generate colors for all actions
np.random.seed(42)
colors = [(np.random.randint(50, 255), np.random.randint(50, 255), np.random.randint(50, 255))
          for _ in range(num_actions)]
print(f"Generated {len(colors)} colors for visualization")

# Get sequence length from model input shape
trained_sequence_length = model.input_shape[1]
# Use shorter sequence for faster recognition
FAST_SEQUENCE_LENGTH = max(10, trained_sequence_length // 2)
print(f"Model trained on: {trained_sequence_length} frames")
print(f"Using for prediction: {FAST_SEQUENCE_LENGTH} frames (faster)")
print("=" * 60 + "\n")

# Detection variables
sequence = []
sentence = []
predictions = []
threshold = 0.7  # Lowered from 0.8 for easier recognition
STABLE_FRAMES = 5  # Reduced from 8 for faster recognition
COOLDOWN_FRAMES = 10  # Reduced from 15
cooldown_counter = 0
last_recognized = None
debug_mode = False  # Disabled by default

print("🎥 Starting camera...")
print("📝 Recognized words appear on SCREEN and in console below:")
print("   (Press C to clear, Q to quit, D for debug)")
print("-" * 60)
print("", end="", flush=True)  # Start on a fresh line for sentence

cap = cv2.VideoCapture(0)
hands_first_detected = False  # Track if we've seen hands for the first time

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    while cap.isOpened():

        ret, frame = cap.read()
        image, results = mediapipe_detection(frame, holistic)
        draw_styled_landmarks(image, results)

        # Check if hand is currently detected
        hand_currently_detected = has_hand(results)

        # Print message when hands first detected (only in debug mode)
        if hand_currently_detected and not hands_first_detected:
            hands_first_detected = True
            if debug_mode:
                print("\n[Hands detected]", flush=True)

        # Handle cooldown
        if cooldown_counter > 0:
            cooldown_counter -= 1

        # Only predict when hands are CURRENTLY visible
        if hand_currently_detected:
            # Prediction logic
            keypoints = extract_keypoints(results)
            sequence.append(keypoints)
            sequence = sequence[-FAST_SEQUENCE_LENGTH:]

            if len(sequence) == FAST_SEQUENCE_LENGTH and cooldown_counter == 0:
                # Pad sequence to match trained length
                padded_sequence = list(sequence)
                last_frame = keypoints
                while len(padded_sequence) < trained_sequence_length:
                    padded_sequence.append(last_frame)

                # Make prediction
                res = model.predict(np.expand_dims(padded_sequence[:trained_sequence_length], axis=0), verbose=0)[0]
                predicted_idx = np.argmax(res)
                confidence = res[predicted_idx]
                predictions.append(predicted_idx)

                # Keep only recent predictions for stability check
                predictions = predictions[-STABLE_FRAMES:]

                # Check if prediction is stable and confident
                if len(predictions) == STABLE_FRAMES:
                    # Check if most recent predictions agree
                    most_common = max(set(predictions), key=list(predictions).count)
                    consistency = list(predictions).count(most_common) / STABLE_FRAMES

                    # LOOSER: Require good confidence OR good consistency
                    if consistency >= 0.6 and res[most_common] > threshold:
                        recognized_action = actions[most_common]

                        # Add to sentence if it's a new word
                        if recognized_action != last_recognized:
                            sentence.append(recognized_action)

                            # Simple console output - just add the word
                            if debug_mode:
                                print(
                                    f"\n[{recognized_action.upper()}] Conf:{res[most_common]:.0%} Cons:{consistency:.0%}",
                                    flush=True)
                            else:
                                # Print with a space, no newline
                                print(f"{recognized_action.upper()} ", end="", flush=True)

                            last_recognized = recognized_action
                            predictions = []  # Clear predictions after recognition
                            sequence = []  # Clear sequence
                            cooldown_counter = COOLDOWN_FRAMES  # Start cooldown

                if len(sentence) > 5:
                    sentence = sentence[-5:]

                # Don't show probability bars - REMOVED
                # image = prob_viz(res, actions, image, colors)

                # Show only top prediction instead of bars
                sorted_indices = np.argsort(res)[::-1]
                top_idx = sorted_indices[0]
                top_action = actions[top_idx]
                top_conf = res[top_idx]

                # Show current detection
                color = (0, 255, 0) if top_conf > threshold else (100, 100, 100)
                cv2.putText(image, f'Detecting: {top_action.upper()}',
                            (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
        else:
            # Clear sequence when no hands detected
            if len(sequence) > 0:
                sequence = []
                predictions = []
                last_recognized = None  # Reset on hand removal
                hands_first_detected = False  # Reset for next time
                # No message when hands removed - keep output clean

            # Display waiting message
            cv2.rectangle(image, (0, 440), (640, 480), (50, 50, 50), -1)
            cv2.putText(image, 'NO HANDS - Show hands to start recognition', (10, 465),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

            # Show word count even when no hands
            if len(sentence) > 0:
                cv2.putText(image, f'Words: {len(sentence)}', (520, 465),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

        # Display sentence on screen - LARGE AND VISIBLE
        sentence_text = ' '.join([s.upper() for s in sentence]) if sentence else ""

        # Background bar for sentence - CHANGED TO DARK BLUE/TEAL
        cv2.rectangle(image, (0, 0), (640, 50), (60, 20, 60), -1)  # Dark purple background

        # Display sentence - scale text if too long - CHANGED TO CYAN/BRIGHT COLOR
        if sentence_text:
            # Calculate text size to fit in window
            max_width = 620
            text_scale = 1.2
            text_thickness = 2

            (text_width, text_height), _ = cv2.getTextSize(sentence_text, cv2.FONT_HERSHEY_SIMPLEX, text_scale,
                                                           text_thickness)

            # Scale down if text is too wide
            if text_width > max_width:
                text_scale = max_width / text_width * text_scale
                text_thickness = max(1, int(text_thickness * 0.8))

            # CHANGED COLOR TO BRIGHT CYAN
            cv2.putText(image, sentence_text, (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, text_scale, (0, 255, 255), text_thickness, cv2.LINE_AA)
        else:
            cv2.putText(image, '[Make signs to start]', (10, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (150, 150, 150), 2, cv2.LINE_AA)

        # Show to screen
        cv2.imshow('Sign Language Detection', image)

        # Keyboard controls
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord('c') or key == ord('C'):
            sentence = []
            last_recognized = None
            print("\n[CLEARED]\n", end="", flush=True)
        elif key == ord('d') or key == ord('D'):
            debug_mode = not debug_mode
            status = "ON" if debug_mode else "OFF"
            print(f"\n[Debug: {status}]\n", end="", flush=True)
        elif key == ord('+') or key == ord('='):
            threshold = min(0.95, threshold + 0.05)
            if debug_mode:
                print(f"\n[Threshold: {threshold:.0%}]\n", end="", flush=True)
        elif key == ord('-') or key == ord('_'):
            threshold = max(0.5, threshold - 0.05)
            if debug_mode:
                print(f"\n[Threshold: {threshold:.0%}]\n", end="", flush=True)

    cap.release()
    cv2.destroyAllWindows()

# Print final sentence
if sentence:
    print("\n\n" + "-" * 60)
    print(f"Final: {' '.join(sentence).upper()}")
    print("-" * 60)
else:
    print("\n\n[No words recognized]")