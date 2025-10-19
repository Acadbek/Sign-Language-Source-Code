# from flask import Flask, render_template, request
# from flask_socketio import SocketIO, emit
# import cv2
# import numpy as np
# import os
# import base64
# from tensorflow.keras.models import load_model
# import mediapipe as mp
#
# app = Flask(__name__)
# app.config['SECRET_KEY'] = 'your-secret-key'
# socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
#
# # Initialize MediaPipe
# mp_holistic = mp.solutions.holistic
# mp_drawing = mp.solutions.drawing_utils
#
# # Load model and actions
# print("Loading model...")
# try:
#     model = load_model('actions_holistic.keras')
#     actions = np.load('actions_holistic_actions.npy')
#     print(f"Model loaded! Actions: {actions}")
# except Exception as e:
#     print(f"Error loading model: {e}")
#     exit()
#
# # Model parameters
# trained_sequence_length = model.input_shape[1]
# FAST_SEQUENCE_LENGTH = max(10, trained_sequence_length // 2)
# threshold = 0.7
# STABLE_FRAMES = 5
# COOLDOWN_FRAMES = 10
#
# # Store sequences per client (use session or client-specific storage in production)
# client_data = {}
#
#
# def mediapipe_detection(image, model):
#     image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     image.flags.writeable = False
#     results = model.process(image)
#     image.flags.writeable = True
#     image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     return image, results
#
#
# def draw_styled_landmarks(image, results):
#     mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS,
#                               mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
#                               mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))
#     mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS,
#                               mp_drawing.DrawingSpec(color=(80, 22, 10), thickness=2, circle_radius=4),
#                               mp_drawing.DrawingSpec(color=(80, 44, 121), thickness=2, circle_radius=2))
#     mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
#                               mp_drawing.DrawingSpec(color=(121, 22, 76), thickness=2, circle_radius=4),
#                               mp_drawing.DrawingSpec(color=(121, 44, 250), thickness=2, circle_radius=2))
#     mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS,
#                               mp_drawing.DrawingSpec(color=(245, 117, 66), thickness=2, circle_radius=4),
#                               mp_drawing.DrawingSpec(color=(245, 66, 230), thickness=2, circle_radius=2))
#
#
# def extract_keypoints(results):
#     pose = np.array([[res.x, res.y, res.z, res.visibility] for res in
#                      results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33 * 4)
#     face = np.array([[res.x, res.y, res.z] for res in
#                      results.face_landmarks.landmark]).flatten() if results.face_landmarks else np.zeros(468 * 3)
#     lh = np.array([[res.x, res.y, res.z] for res in
#                    results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21 * 3)
#     rh = np.array([[res.x, res.y, res.z] for res in
#                    results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(
#         21 * 3)
#     return np.concatenate([pose, face, lh, rh])
#
#
# def has_hand(results):
#     return results.left_hand_landmarks is not None or results.right_hand_landmarks is not None
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @socketio.on('connect')
# def handle_connect():
#     from flask import request
#     print(f'Client connected: {request.sid}')
#     # Initialize client data
#     client_data[request.sid] = {
#         'sequence': [],
#         'predictions': [],
#         'sentence': [],
#         'last_recognized': None,
#         'cooldown_counter': 0,
#         'holistic': mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#     }
#
#
# @socketio.on('disconnect')
# def handle_disconnect():
#     from flask import request
#     print(f'Client disconnected: {request.sid}')
#     if request.sid in client_data:
#         client_data[request.sid]['holistic'].close()
#         del client_data[request.sid]
#
#
# @socketio.on('video_frame')
# def handle_video_frame(data):
#     from flask import request
#     sid = request.sid
#
#     if sid not in client_data:
#         return
#
#     cd = client_data[sid]
#
#     # Decode base64 image
#     img_data = base64.b64decode(data['image'].split(',')[1])
#     nparr = np.frombuffer(img_data, np.uint8)
#     frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#
#     # Process with MediaPipe
#     image, results = mediapipe_detection(frame, cd['holistic'])
#     draw_styled_landmarks(image, results)
#
#     hand_detected = has_hand(results)
#     recognized_word = None
#
#     # Handle cooldown
#     if cd['cooldown_counter'] > 0:
#         cd['cooldown_counter'] -= 1
#
#     if hand_detected:
#         keypoints = extract_keypoints(results)
#         cd['sequence'].append(keypoints)
#         cd['sequence'] = cd['sequence'][-FAST_SEQUENCE_LENGTH:]
#
#         if len(cd['sequence']) == FAST_SEQUENCE_LENGTH and cd['cooldown_counter'] == 0:
#             # Pad sequence
#             padded_sequence = list(cd['sequence'])
#             last_frame = keypoints
#             while len(padded_sequence) < trained_sequence_length:
#                 padded_sequence.append(last_frame)
#
#             # Predict
#             res = model.predict(np.expand_dims(padded_sequence[:trained_sequence_length], axis=0), verbose=0)[0]
#             predicted_idx = np.argmax(res)
#             confidence = res[predicted_idx]
#             cd['predictions'].append(predicted_idx)
#             cd['predictions'] = cd['predictions'][-STABLE_FRAMES:]
#
#             if len(cd['predictions']) == STABLE_FRAMES:
#                 most_common = max(set(cd['predictions']), key=list(cd['predictions']).count)
#                 consistency = list(cd['predictions']).count(most_common) / STABLE_FRAMES
#
#                 if consistency >= 0.6 and res[most_common] > threshold:
#                     recognized_action = actions[most_common]
#
#                     if recognized_action != cd['last_recognized']:
#                         cd['sentence'].append(recognized_action)
#                         recognized_word = recognized_action
#                         cd['last_recognized'] = recognized_action
#                         cd['predictions'] = []
#                         cd['sequence'] = []
#                         cd['cooldown_counter'] = COOLDOWN_FRAMES
#
#             if len(cd['sentence']) > 5:
#                 cd['sentence'] = cd['sentence'][-5:]
#
#             # Show detection
#             top_idx = np.argmax(res)
#             top_action = actions[top_idx]
#             top_conf = res[top_idx]
#             color = (0, 255, 0) if top_conf > threshold else (100, 100, 100)
#             cv2.putText(image, f'Detecting: {top_action.upper()}',
#                         (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)
#
#         status = f'COOLDOWN {cd["cooldown_counter"]}' if cd[
#                                                              'cooldown_counter'] > 0 else f'{len(cd["sequence"])}/{FAST_SEQUENCE_LENGTH} frames'
#         cv2.putText(image, f'HAND DETECTED - {status}', (10, 445),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
#         cv2.putText(image, f'Words: {len(cd["sentence"])}', (10, 470),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
#     else:
#         if len(cd['sequence']) > 0:
#             cd['sequence'] = []
#             cd['predictions'] = []
#             cd['last_recognized'] = None
#
#         cv2.rectangle(image, (0, 440), (640, 480), (50, 50, 50), -1)
#         cv2.putText(image, 'NO HANDS - Show hands to start recognition', (10, 465),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)
#
#         if len(cd['sentence']) > 0:
#             cv2.putText(image, f'Words: {len(cd["sentence"])}', (520, 465),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
#
#     # Display sentence
#     sentence_text = ' '.join([s.upper() for s in cd['sentence']]) if cd['sentence'] else ""
#     cv2.rectangle(image, (0, 0), (640, 50), (60, 20, 60), -1)
#
#     if sentence_text:
#         cv2.putText(image, sentence_text, (10, 35),
#                     cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2, cv2.LINE_AA)
#     else:
#         cv2.putText(image, '[Make signs to start]', (10, 35),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.9, (150, 150, 150), 2, cv2.LINE_AA)
#
#     # Encode processed frame
#     _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 80])
#     frame_base64 = base64.b64encode(buffer).decode('utf-8')
#
#     # Send back processed frame and sentence
#     emit('processed_frame', {
#         'image': f'data:image/jpeg;base64,{frame_base64}',
#         'sentence': sentence_text,
#         'recognized_word': recognized_word
#     })
#
#
# @socketio.on('clear_sentence')
# def handle_clear():
#     from flask import request
#     sid = request.sid
#     if sid in client_data:
#         client_data[sid]['sentence'] = []
#         client_data[sid]['last_recognized'] = None
#         print('Sentence cleared')
#
#
# if __name__ == '__main__':
#     print("Starting Flask-SocketIO server...")
#     print(f"Model: {len(actions)} actions, {trained_sequence_length} frames")
#     print(f"Using: {FAST_SEQUENCE_LENGTH} frames for prediction")
#     socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)


from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import numpy as np
import os
import base64
from tensorflow.keras.models import load_model
import mediapipe as mp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app)  # Enable CORS for all HTTP routes
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ADD THIS: Security headers middleware
@app.after_request
def add_security_headers(response):
    """Add required OWASP security headers for Zoom Apps"""
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' "
        "https://appssdk.zoom.us https://*.zoom.us "
        "https://cdn.socket.io https://cdn.jsdelivr.net "
        "data: blob: ws: wss:; "
        "frame-ancestors 'self' https://*.zoom.us"
    )
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

# Initialize MediaPipe
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Load model and actions
print("Loading model...")
try:
    model = load_model('actions_holistic.keras')
    actions = np.load('actions_holistic_actions.npy')
    print(f"Model loaded! Actions: {actions}")
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Model parameters
trained_sequence_length = model.input_shape[1]
FAST_SEQUENCE_LENGTH = max(10, trained_sequence_length // 2)
threshold = 0.1  # Lowered from 0.7 to 0.4 for better detection
STABLE_FRAMES = 5
COOLDOWN_FRAMES = 10

# Store sequences per client (use session or client-specific storage in production)
client_data = {}


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


def has_hand(results):
    return results.left_hand_landmarks is not None or results.right_hand_landmarks is not None


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    from flask import request
    print(f'Client connected: {request.sid}')
    # Initialize client data
    client_data[request.sid] = {
        'sequence': [],
        'predictions': [],
        'sentence': [],
        'last_recognized': None,
        'cooldown_counter': 0,
        'holistic': mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    }


@socketio.on('disconnect')
def handle_disconnect():
    from flask import request
    print(f'Client disconnected: {request.sid}')
    if request.sid in client_data:
        client_data[request.sid]['holistic'].close()
        del client_data[request.sid]


frame_receive_count = {}

@socketio.on('video_frame')
def handle_video_frame(data):
    from flask import request
    sid = request.sid

    # DEBUG: Count received frames
    if sid not in frame_receive_count:
        frame_receive_count[sid] = 0
    frame_receive_count[sid] += 1

    if frame_receive_count[sid] % 30 == 0:
        print(f'[RECV] Received {frame_receive_count[sid]} frames from client {sid}')

    if sid not in client_data:
        print(f'[ERROR] Client {sid} not in client_data!')
        return

    cd = client_data[sid]

    # Decode base64 image
    try:
        img_data = base64.b64decode(data['image'].split(',')[1])
        nparr = np.frombuffer(img_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            print(f'[ERROR] Failed to decode frame for {sid}')
            return
    except Exception as e:
        print(f'[ERROR] Frame decode error: {e}')
        return

    # Process with MediaPipe
    image, results = mediapipe_detection(frame, cd['holistic'])
    draw_styled_landmarks(image, results)

    hand_detected = has_hand(results)
    recognized_word = None

    # DEBUG: Log hand detection every 30 frames
    if frame_receive_count[sid] % 30 == 0:
        print(f'[PROC] Frame #{frame_receive_count[sid]} - Hands detected: {hand_detected}, Sentence list: {cd["sentence"]}')

    # Handle cooldown
    if cd['cooldown_counter'] > 0:
        cd['cooldown_counter'] -= 1

    # Track current top prediction
    top_prediction = None
    top_confidence = 0.0

    if hand_detected:
        keypoints = extract_keypoints(results)
        cd['sequence'].append(keypoints)
        cd['sequence'] = cd['sequence'][-FAST_SEQUENCE_LENGTH:]

        if len(cd['sequence']) == FAST_SEQUENCE_LENGTH and cd['cooldown_counter'] == 0:
            # Pad sequence
            padded_sequence = list(cd['sequence'])
            last_frame = keypoints
            while len(padded_sequence) < trained_sequence_length:
                padded_sequence.append(last_frame)

            # Predict
            res = model.predict(np.expand_dims(padded_sequence[:trained_sequence_length], axis=0), verbose=0)[0]
            predicted_idx = np.argmax(res)
            confidence = res[predicted_idx]
            predicted_action = actions[predicted_idx]

            # DEBUG: Show prediction details
            if frame_receive_count[sid] % 30 == 0:
                print(f'[PRED] Top prediction: {predicted_action} (conf: {confidence:.2f}, threshold: {threshold})')

            cd['predictions'].append(predicted_idx)
            cd['predictions'] = cd['predictions'][-STABLE_FRAMES:]

            if len(cd['predictions']) == STABLE_FRAMES:
                most_common = max(set(cd['predictions']), key=list(cd['predictions']).count)
                consistency = list(cd['predictions']).count(most_common) / STABLE_FRAMES
                most_common_action = actions[most_common]
                most_common_conf = res[most_common]

                print(f'[EVAL] Action: {most_common_action} | Consistency: {consistency:.2f} (need 0.6) | Conf: {most_common_conf:.2f} (need {threshold})')

                if consistency >= 0.6 and res[most_common] > threshold:
                    recognized_action = actions[most_common]

                    if recognized_action != cd['last_recognized']:
                        cd['sentence'].append(recognized_action)
                        recognized_word = recognized_action
                        cd['last_recognized'] = recognized_action
                        cd['predictions'] = []
                        cd['sequence'] = []
                        cd['cooldown_counter'] = COOLDOWN_FRAMES
                        print(f'[RECOG] ✨ NEW WORD: {recognized_action} | Full sentence: {cd["sentence"]}')
                else:
                    print(f'[REJECT] Not confident enough - consistency: {consistency:.2f}, conf: {most_common_conf:.2f}')

            if len(cd['sentence']) > 5:
                cd['sentence'] = cd['sentence'][-5:]

            # Show detection
            top_idx = np.argmax(res)
            top_action = actions[top_idx]
            top_conf = res[top_idx]

            # Store for sending to frontend
            top_prediction = top_action.upper()
            top_confidence = float(top_conf)

            color = (0, 255, 0) if top_conf > threshold else (100, 100, 100)
            cv2.putText(image, f'Detecting: {top_action.upper()}',
                        (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2, cv2.LINE_AA)

        status = f'COOLDOWN {cd["cooldown_counter"]}' if cd[
                                                             'cooldown_counter'] > 0 else f'{len(cd["sequence"])}/{FAST_SEQUENCE_LENGTH} frames'
        cv2.putText(image, f'HAND DETECTED - {status}', (10, 445),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(image, f'Words: {len(cd["sentence"])}', (10, 470),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
    else:
        if len(cd['sequence']) > 0:
            cd['sequence'] = []
            cd['predictions'] = []
            cd['last_recognized'] = None

        cv2.rectangle(image, (0, 440), (640, 480), (50, 50, 50), -1)
        cv2.putText(image, 'NO HANDS - Show hands to start recognition', (10, 465),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2, cv2.LINE_AA)

        if len(cd['sentence']) > 0:
            cv2.putText(image, f'Words: {len(cd["sentence"])}', (520, 465),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)

    # Display sentence
    sentence_text = ' '.join([s.upper() for s in cd['sentence']]) if cd['sentence'] else ""
    cv2.rectangle(image, (0, 0), (640, 50), (60, 20, 60), -1)

    if sentence_text:
        cv2.putText(image, sentence_text, (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 2, cv2.LINE_AA)
    else:
        cv2.putText(image, '[Make signs to start]', (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (150, 150, 150), 2, cv2.LINE_AA)

    # Encode processed frame with moderate quality
    _, buffer = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, 75])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')

    # Send back processed frame and sentence
    result = {
        'image': f'data:image/jpeg;base64,{frame_base64}',
        'sentence': sentence_text,
        'recognized_word': recognized_word,
        'detecting': top_prediction,  # Current top prediction (even if not confident enough)
        'confidence': top_confidence  # Confidence level
    }

    # DEBUG: Print what we're sending
    if sentence_text or recognized_word or top_prediction:
        print(f'[SEND] Sentence: "{sentence_text}" | Recognized: {recognized_word} | Detecting: {top_prediction} ({top_confidence:.2f})')

    emit('processed_frame', result)


@socketio.on('clear_sentence')
def handle_clear():
    from flask import request
    sid = request.sid
    if sid in client_data:
        client_data[sid]['sentence'] = []
        client_data[sid]['last_recognized'] = None
        print('Sentence cleared')


if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    print(f"Model: {len(actions)} actions, {trained_sequence_length} frames")
    print(f"Using: {FAST_SEQUENCE_LENGTH} frames for prediction")
    socketio.run(app, host='0.0.0.0', port=8001, debug=True, allow_unsafe_werkzeug=True)