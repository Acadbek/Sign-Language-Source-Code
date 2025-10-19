import cv2
import numpy as np
import os
import time
import mediapipe as mp
import random

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
                              mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))
    # Draw pose connections
    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))
    # Draw left hand connections
    mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2))
    # Draw right hand connections
    mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
                              mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
                              mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))


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


# Path for exported data
DATA_PATH = os.path.join('MP_Data')

print("=" * 60)
print("IMPROVED DATA COLLECTION - ANTI-OVERFITTING")
print("=" * 60)

# Get words from user
print("\nEnter the words you want to collect data for.")
print("Type 'done' when finished entering words.")
actions = []
while True:
    word = input("Enter word: ").strip().lower()
    if word == 'done':
        break
    if word and word not in actions:
        actions.append(word)
        print(f"✅ Added: {word}")
    elif word in actions:
        print(f"❌ {word} already added!")

if not actions:
    print("No words entered. Using default: ['hello', 'thanks', 'iloveyou']")
    actions = ['hello', 'thanks', 'iloveyou']

actions = np.array(actions)

# Get number of sequences
while True:
    try:
        no_sequences = int(input("\nNumber of sequences per word (recommended: 50+): "))
        if no_sequences > 0:
            break
        print("Please enter a positive number.")
    except ValueError:
        print("Please enter a valid number.")

# Get sequence length (number of frames)
while True:
    try:
        sequence_length = int(input("Frames per sequence (recommended: 30): "))
        if sequence_length > 0:
            break
        print("Please enter a positive number.")
    except ValueError:
        print("Please enter a valid number.")

print("\n" + "=" * 60)
print("COLLECTION STRATEGY")
print("=" * 60)
print(f"✅ Words: {', '.join(actions)}")
print(f"✅ Sequences per word: {no_sequences}")
print(f"✅ Frames per sequence: {sequence_length}")
print(f"✅ Total sequences: {len(actions) * no_sequences}")
print("\n🎯 ANTI-OVERFITTING MEASURES:")
print("   1. Randomized collection order")
print("   2. Forced breaks between sequences")
print("   3. Variation prompts (position, speed, angle)")
print("=" * 60)

# Create directories for each action
for action in actions:
    for sequence in range(no_sequences):
        try:
            os.makedirs(os.path.join(DATA_PATH, action, str(sequence)))
        except:
            pass

# Create randomized collection order
collection_order = []
for action in actions:
    for sequence in range(no_sequences):
        collection_order.append((action, sequence))

# CRITICAL: Shuffle to prevent temporal bias
random.shuffle(collection_order)
print(f"\n✅ Shuffled {len(collection_order)} sequences for random collection")

# Variation prompts
variation_prompts = [
    "Move LEFT in frame",
    "Move RIGHT in frame",
    "Move CLOSER to camera",
    "Move FURTHER from camera",
    "Sign SLOWLY",
    "Sign QUICKLY",
    "Tilt head SLIGHTLY",
    "Change LIGHTING (adjust position)",
]

input("\n🎬 Press ENTER to start data collection...")

# Start data collection
cap = cv2.VideoCapture(0)
collected_count = 0

with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    for action, sequence in collection_order:
        # Pick a random variation prompt
        variation = random.choice(variation_prompts)

        print(f"\n📹 [{collected_count + 1}/{len(collection_order)}] Collecting: {action.upper()} (seq {sequence})")
        print(f"   💡 Variation: {variation}")

        # Wait for spacebar to start
        waiting = True
        while waiting:
            ret, frame = cap.read()
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            # Display instructions
            cv2.rectangle(image, (0, 0), (640, 150), (0, 0, 0), -1)
            cv2.putText(image, 'PRESS SPACE TO START', (80, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3, cv2.LINE_AA)
            cv2.putText(image, f'Word: {action.upper()}', (20, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'Seq: {sequence + 1}/{no_sequences}', (20, 120),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, f'TIP: {variation}', (20, 145),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

            # Progress bar
            progress = collected_count / len(collection_order)
            cv2.rectangle(image, (10, 460), (630, 470), (50, 50, 50), -1)
            cv2.rectangle(image, (10, 460), (10 + int(620 * progress), 470), (0, 255, 0), -1)
            cv2.putText(image, f'{collected_count}/{len(collection_order)}', (540, 465),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

            cv2.imshow('Data Collection', image)

            key = cv2.waitKey(10)
            if key == 32:  # Space key
                waiting = False
            elif key == ord('q'):
                cap.release()
                cv2.destroyAllWindows()
                print("\n❌ Collection cancelled by user")
                exit()

        # Countdown before recording
        for countdown in range(3, 0, -1):
            ret, frame = cap.read()
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            cv2.putText(image, str(countdown), (280, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5, cv2.LINE_AA)
            cv2.imshow('Data Collection', image)
            cv2.waitKey(1000)

        # Record sequence
        for frame_num in range(sequence_length):
            ret, frame = cap.read()
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            # Display recording status
            cv2.rectangle(image, (0, 0), (640, 100), (0, 0, 255), -1)
            cv2.putText(image, 'RECORDING...', (200, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
            cv2.putText(image, f'{action.upper()} - Frame {frame_num + 1}/{sequence_length}', (150, 75),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

            # Progress bar for current sequence
            frame_progress = (frame_num + 1) / sequence_length
            cv2.rectangle(image, (50, 110), (590, 130), (50, 50, 50), -1)
            cv2.rectangle(image, (50, 110), (50 + int(540 * frame_progress), 130), (0, 255, 0), -1)

            cv2.imshow('Data Collection', image)
            cv2.waitKey(33)  # ~30 FPS

            # Save keypoints
            keypoints = extract_keypoints(results)
            npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
            np.save(npy_path, keypoints)

        collected_count += 1

        # Mandatory break between sequences (1.5 seconds)
        for i in range(15):
            ret, frame = cap.read()
            image, results = mediapipe_detection(frame, holistic)
            draw_styled_landmarks(image, results)

            cv2.rectangle(image, (0, 0), (640, 100), (0, 165, 255), -1)
            cv2.putText(image, 'BREAK - Relax & Reset', (120, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(image, 'Change position/angle for next sequence', (80, 85),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow('Data Collection', image)
            cv2.waitKey(100)

    cap.release()
    cv2.destroyAllWindows()

print("\n" + "=" * 60)
print("DATA COLLECTION COMPLETE! 🎉")
print("=" * 60)
print(f"📁 Data saved in: {DATA_PATH}")
print(f"✅ Total sequences collected: {len(collection_order)}")
print(f"📊 Sequences per word: {no_sequences}")
print("\n💡 Next steps:")
print("   1. Review your data quality")
print("   2. Train model with CustomNeuralNetwork.py")
print("   3. Test with Run.py")
print("=" * 60)