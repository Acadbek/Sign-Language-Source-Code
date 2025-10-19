# 🏗️ System Architecture

## Overview

The integrated system combines three independent components:
1. Sign Language Recognition (Flask + Socket.IO)
2. Speech-to-Sign Translation (Flask + NVIDIA NeMo)
3. Jitsi Video Conferencing (External API)

---

## Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                              │
│                                                                    │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │           jitsi-combined-app.html (HTML/JS)                  │ │
│  │                                                              │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌───────────────┐ │ │
│  │  │ Sign Language  │  │ Jitsi Video    │  │ Speech-to-Sign│ │ │
│  │  │ Panel          │  │ Conference     │  │ Panel         │ │ │
│  │  │                │  │                │  │               │ │ │
│  │  │ - Camera feed  │  │ - iframe       │  │ - Mic input   │ │ │
│  │  │ - Captions     │  │ - External API │  │ - Uzbek text  │ │ │
│  │  │ - Share button │  │ - Chat         │  │ - Letters     │ │ │
│  │  └────────┬───────┘  └────────┬───────┘  └───────┬───────┘ │ │
│  │           │                   │                   │         │ │
│  └───────────┼───────────────────┼───────────────────┼─────────┘ │
│              │                   │                   │           │
└──────────────┼───────────────────┼───────────────────┼───────────┘
               │                   │                   │
               ▼                   ▼                   ▼
   ┌───────────────────┐  ┌───────────────┐  ┌──────────────────┐
   │ Flask Backend #1  │  │ Jitsi Servers │  │ Flask Backend #2 │
   │ (signToText)      │  │ meet.jit.si   │  │ (speachToSign)   │
   │                   │  │               │  │                  │
   │ Port: 5000        │  │ Public Cloud  │  │ Port: 7860       │
   │ Protocol:         │  │               │  │ Protocol: HTTP   │
   │   Socket.IO       │  │               │  │                  │
   │                   │  │               │  │                  │
   │ ┌───────────────┐ │  │               │  │ ┌──────────────┐ │
   │ │ MediaPipe     │ │  │               │  │ │ NVIDIA NeMo  │ │
   │ │ Holistic      │ │  │               │  │ │ FastConformer│ │
   │ └───────────────┘ │  │               │  │ └──────────────┘ │
   │ ┌───────────────┐ │  │               │  │                  │
   │ │ LSTM Model    │ │  │               │  │                  │
   │ │ (Keras)       │ │  │               │  │                  │
   │ └───────────────┘ │  │               │  │                  │
   └───────────────────┘  └───────────────┘  └──────────────────┘
```

---

## Component Details

### 1. Sign Language Recognition Backend

**File:** `signToText/app.py`

**Technology Stack:**
- Flask (web framework)
- Flask-SocketIO (WebSocket communication)
- MediaPipe (pose/hand/face detection)
- TensorFlow/Keras (LSTM model)
- OpenCV (image processing)

**Data Flow:**
1. Browser captures video from webcam
2. Converts frame to base64 JPEG
3. Sends via Socket.IO to Flask backend (port 5000)
4. Backend processes with MediaPipe (extracts 1,662 keypoints)
5. LSTM model predicts sign from keypoint sequence
6. Returns processed frame + recognized text
7. Browser displays processed video and captions

**Communication:**
- Protocol: Socket.IO (WebSocket)
- Events:
  - `connect` - Initialize client session
  - `video_frame` - Send frame for processing
  - `processed_frame` - Receive results
  - `clear_sentence` - Clear recognized text
  - `disconnect` - Cleanup

**Performance:**
- Processes every 2nd frame (CPU optimization)
- ~100ms latency per frame
- JPEG quality: 75% (bandwidth optimization)

---

### 2. Speech-to-Sign Backend

**File:** `speachToSign/app.py`

**Technology Stack:**
- Flask (web framework)
- NVIDIA NeMo (speech recognition)
- Librosa (audio processing)
- SoundFile (audio I/O)

**Data Flow:**
1. Browser records audio in 3-second chunks
2. Sends audio file (WebM format) via HTTP POST
3. Backend converts to 16kHz mono WAV
4. NVIDIA FastConformer transcribes (Uzbek)
5. Converts text to fingerspelling letters
6. Returns transcription + animation data
7. Browser displays text and letters

**Communication:**
- Protocol: HTTP (REST API)
- Endpoints:
  - `GET /` - Serve web interface
  - `POST /transcribe` - Transcribe audio
  - `GET /message` - Unity endpoint
  - `GET /health` - Server status

**Model:**
- Name: `nvidia/stt_uz_fastconformer_hybrid_large_pc`
- Language: Uzbek
- WER: 16.46%
- Size: ~500 MB (downloads on first run)

---

### 3. Jitsi Video Conference

**File:** `jitsi-combined-app.html` (embedded)

**Technology:**
- Jitsi External API
- iframe embedding
- JavaScript event handling

**Integration:**
- Uses public Jitsi server (meet.jit.si)
- No backend required
- Pure client-side integration

**Features:**
- Video/audio calls
- Screen sharing
- Chat (receives captions)
- Participant management

**Communication:**
- Protocol: WebRTC (peer-to-peer)
- API: JavaScript commands
- Methods:
  - `executeCommand('sendChatMessage', text)` - Send caption
  - `addEventListener('participantJoined', callback)` - Track users

---

## Data Flow: Sign-to-Text-to-Jitsi

```
[User Makes Sign]
       ↓
[Browser Captures Frame]
       ↓
[Convert to Base64]
       ↓
[Socket.IO → Port 5000]
       ↓
[MediaPipe Keypoint Extraction]
       ↓
[LSTM Inference]
       ↓
[Recognized Text]
       ↓
[Socket.IO ← Port 5000]
       ↓
[Display in Caption Box]
       ↓
[User Clicks "Share to Jitsi"]
       ↓
[Jitsi API: sendChatMessage()]
       ↓
[All Participants See in Chat]
```

---

## Data Flow: Speech-to-Letters-to-Jitsi

```
[User Speaks (Uzbek)]
       ↓
[Browser Records Audio (3s chunks)]
       ↓
[Convert to WebM Blob]
       ↓
[HTTP POST → Port 7860]
       ↓
[Librosa Audio Processing]
       ↓
[NVIDIA NeMo Transcription]
       ↓
[Text-to-Fingerspelling Conversion]
       ↓
[HTTP Response ← Port 7860]
       ↓
[Display Text + Letters]
       ↓
[User Clicks "Share to Jitsi"]
       ↓
[Jitsi API: sendChatMessage()]
       ↓
[All Participants See in Chat]
```

---

## Network Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Sign Language Backend | 5000 | Socket.IO (WebSocket) | Video frame processing |
| Speech Backend | 7860 | HTTP | Audio transcription |
| Web Server (optional) | 8000 | HTTP | Serve HTML file |
| Jitsi | 443 | HTTPS/WebRTC | Video conferencing |

---

## Security Considerations

### Current Setup (Development)
- ✅ CORS enabled for all origins (`*`)
- ✅ Local processing (video stays on your machine)
- ❌ HTTP (not HTTPS)
- ❌ No authentication
- ❌ Public Jitsi server (meet.jit.si)

### Production Recommendations
- 🔒 Configure CORS for specific domains only
- 🔒 Use HTTPS with SSL certificates
- 🔒 Add user authentication
- 🔒 Deploy own Jitsi server
- 🔒 Rate limiting on API endpoints
- 🔒 Input validation and sanitization

---

## Scalability

### Current Limitations
- **Sign Language Backend:**
  - CPU-bound (MediaPipe + LSTM)
  - ~10-20 concurrent users per server
  - No horizontal scaling (stateful Socket.IO)

- **Speech Backend:**
  - GPU recommended for NVIDIA NeMo
  - ~5-10 concurrent users per server
  - Model loading takes ~500 MB RAM

### Scaling Recommendations
1. Use Redis for Socket.IO session storage
2. Deploy multiple backend instances
3. Use load balancer with sticky sessions
4. Add GPU acceleration for speech processing
5. Implement request queuing
6. Cache model predictions

---

## Technology Choices Explained

### Why Flask?
- ✅ Your existing code uses Flask
- ✅ Python ecosystem for ML (TensorFlow, NeMo)
- ✅ Easy to integrate with MediaPipe
- ❌ Not the fastest (but sufficient for MVP)

### Why Socket.IO?
- ✅ Real-time bidirectional communication
- ✅ Automatic reconnection
- ✅ Works well for video streaming
- ✅ Your existing code uses it

### Why Jitsi External API?
- ✅ No backend needed
- ✅ Production-ready video conferencing
- ✅ Free public server
- ✅ Easy integration
- ✅ No modification to Jitsi source code

---

## Future Enhancements

### Possible Improvements
1. **Client-Side Processing:** Convert to TensorFlow.js (eliminates backend)
2. **WebRTC Insertable Streams:** Direct video pipeline processing
3. **Multiple Languages:** Add more speech recognition models
4. **Custom Gestures:** Train on custom sign language dataset
5. **Real-Time Subtitles:** Overlay on Jitsi video
6. **Mobile Apps:** React Native integration

---

## Deployment Options

### Option 1: Local (Current)
- Run on localhost
- Users must access your IP address
- No cloud costs
- Limited to local network

### Option 2: Cloud VPS
- Deploy to AWS/GCP/Azure
- Public access
- Requires server management
- ~$50-100/month

### Option 3: Containerized (Docker)
- Package all services in containers
- Easy deployment
- Scalable
- Recommended for production

---

## Performance Metrics

### Sign Language Recognition
- **Latency:** ~100-150ms per frame
- **Accuracy:** Depends on trained model
- **Frame Rate:** ~10 FPS (processed)
- **Bandwidth:** ~1-2 MB/s per user

### Speech Recognition
- **Latency:** ~1-3 seconds per chunk
- **Accuracy:** WER 16.46% (Uzbek)
- **Audio Quality:** 16kHz mono
- **Model Size:** ~500 MB

### Jitsi
- **Video Quality:** Up to 720p
- **Participants:** 10-100 (depends on server)
- **Latency:** ~100-300ms (P2P mode)

---

This architecture provides a solid foundation for real-time sign language and speech recognition integrated with video conferencing, while keeping your existing Flask backends intact and working!
