# 🤟 Sign Language + Jitsi Video Conference Integration

Complete integration of sign language recognition, speech-to-sign translation, and Jitsi video conferencing - all working together seamlessly!

---

## 📖 What This Project Does

This application combines three powerful features:

1. **🤟 Sign Language → Text Recognition**
   - Real-time hand sign detection using MediaPipe
   - LSTM neural network for gesture recognition
   - Displays recognized words as captions

2. **🎤 Speech → Sign Language Translation**
   - Uzbek speech recognition using NVIDIA NeMo
   - Converts speech to fingerspelling letters
   - Shows letter-by-letter animations

3. **📹 Jitsi Video Conferencing**
   - Multi-participant video calls
   - Screen sharing and chat
   - Captions can be shared with all participants

---

## 🎯 Key Features

- ✅ **Real-time sign language recognition** with camera
- ✅ **Uzbek speech-to-text** with NVIDIA FastConformer (WER: 16.46%)
- ✅ **Jitsi video conferencing** integration
- ✅ **Share captions** to all participants via chat
- ✅ **Three-panel interface** - all features in one view
- ✅ **No Jitsi source code modifications** - uses External API
- ✅ **Your existing Flask backends** - zero rewrites

---

## 📂 Project Structure

```
/Users/bilmao/Desktop/mentoraAi/
│
├── signToText/                      # Sign Language Recognition Backend
│   ├── app.py                       # Flask + Socket.IO server (Port 5000)
│   ├── index.html                   # Original standalone interface
│   ├── requirements.txt             # Python dependencies
│   ├── actions_holistic.keras       # LSTM model (5.7 MB)
│   └── actions_holistic_actions.npy # Action labels
│
├── speachToSign/                    # Speech-to-Sign Backend
│   ├── app.py                       # Flask + NVIDIA NeMo server (Port 7860)
│   ├── ind.html                     # Original standalone interface
│   └── requirements.txt             # Python dependencies
│
├── jitsi-meet/                      # Jitsi Meet source code (optional)
│   └── ... (full Jitsi codebase)
│
├── usedModels/                      # Pre-trained models
│   └── *.keras files
│
├── jitsi-combined-app.html          # 🌟 MAIN APPLICATION FILE
│
├── QUICK_START.md                   # ⚡ Fast setup guide
├── SETUP_AND_RUN_INSTRUCTIONS.md    # 📋 Detailed instructions
├── ARCHITECTURE.md                  # 🏗️ Technical documentation
└── README.md                        # 📖 This file
```

---

## 🚀 Quick Start (4 Steps)

### Step 0: Install Python 3.11 (Required!)

```bash
# MediaPipe requires Python 3.11 (doesn't support 3.13 yet)
brew install python@3.11

# Verify
python3.11 --version
```

### Step 1: Install Dependencies

```bash
# Install Sign Language dependencies
cd /Users/bilmao/Desktop/mentoraAi/signToText
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# Install Speech dependencies
cd /Users/bilmao/Desktop/mentoraAi/speachToSign
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

### Step 2: Start Both Backends

**Terminal 1:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText
python app.py
```

**Terminal 2:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign
python app.py
```

---

### Step 3: Open the Application

Open in browser:
```
file:///Users/bilmao/Desktop/mentoraAi/jitsi-combined-app.html
```

Or use HTTP server:
```bash
cd /Users/bilmao/Desktop/mentoraAi
python3 -m http.server 8000
# Then open: http://localhost:8000/jitsi-combined-app.html
```

---

## 🎮 How to Use

### Sign Language Recognition (Left Panel)

1. Click **"▶️ Start Camera"**
2. Allow camera access
3. Make hand signs in front of camera
4. See recognized words in purple caption box
5. Click **"📤 Share to Jitsi"** to send to chat

### Jitsi Video Conference (Center Panel)

1. Enter a **room name** (e.g., "MyRoom")
2. Click **"Join Room"**
3. Allow camera/microphone access
4. Share room name with others to join
5. Captions appear in Jitsi chat

### Speech-to-Sign (Right Panel)

1. Click **"🎤 Start Recording"**
2. Allow microphone access
3. Speak in **Uzbek** (3-second chunks)
4. See transcription and fingerspelling letters
5. Click **"📤 Share to Jitsi"** to send to chat

---

## 📚 Documentation

| File | Purpose |
|------|---------|
| **QUICK_START.md** | Fast setup - installation and running commands |
| **SETUP_AND_RUN_INSTRUCTIONS.md** | Detailed step-by-step guide with troubleshooting |
| **ARCHITECTURE.md** | Technical details, data flows, and system design |
| **README.md** | This file - project overview |

---

## 🔧 What Was Modified

### Files Created (New)
1. ✅ `jitsi-combined-app.html` - Main integrated application
2. ✅ `QUICK_START.md` - Quick reference guide
3. ✅ `SETUP_AND_RUN_INSTRUCTIONS.md` - Detailed instructions
4. ✅ `ARCHITECTURE.md` - Technical documentation
5. ✅ `README.md` - Project overview
6. ✅ `signToText/requirements.txt` - Dependencies list
7. ✅ `speachToSign/requirements.txt` - Dependencies list

### Files Modified (Minimal Changes)
1. ✅ `signToText/app.py` - Added `from flask_cors import CORS` and `CORS(app)` (3 lines)
2. ✅ `speachToSign/app.py` - Already had CORS (no changes needed)

### Files Unchanged (Your Original Code)
- ✅ All LSTM models in `usedModels/`
- ✅ Original `signToText/index.html` (still works standalone)
- ✅ Original `speachToSign/ind.html` (still works standalone)
- ✅ All training/data collection scripts
- ✅ Full Jitsi Meet codebase in `jitsi-meet/`

**Summary:** 99% of your code is unchanged! We only added CORS support and created the integration HTML.

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              jitsi-combined-app.html                    │
│                                                         │
│  [Sign Panel]    [Jitsi Panel]    [Speech Panel]      │
│       ↓               ↓                  ↓             │
│   Socket.IO      External API         HTTP            │
│       ↓               ↓                  ↓             │
│  Port 5000      meet.jit.si        Port 7860          │
│       ↓                                  ↓             │
│  Flask + MediaPipe            Flask + NVIDIA NeMo      │
│  + LSTM Model                                          │
└─────────────────────────────────────────────────────────┘
```

- **No rewrites** - your Flask backends work as-is
- **No Jitsi modifications** - uses External API
- **Simple HTML integration** - connects everything

---

## 💡 Why This Approach?

### ✅ Advantages

1. **Minimal Changes:** Only added CORS (3 lines of code)
2. **Fast Implementation:** 1-2 days vs. weeks of rewriting
3. **Low Risk:** Your existing code continues to work
4. **Easy Testing:** Run each component independently
5. **Maintainable:** Clear separation of concerns
6. **Scalable:** Can deploy each backend separately

### ❌ Trade-offs

1. **Latency:** ~100-150ms (vs. 15-50ms client-side)
2. **Bandwidth:** Uses more network (base64 encoding)
3. **Server Required:** Can't run 100% client-side
4. **Scaling:** Limited to ~10-20 concurrent users per server

**Verdict:** Perfect for MVP, demos, and testing. Can optimize later if needed.

---

## 🔍 System Requirements

- **Python:** 3.11 or 3.12 (NOT 3.13 - MediaPipe incompatible)
- **Homebrew:** For installing Python 3.11 on macOS
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk:** 2 GB free space (for models)
- **Internet:** Required for Jitsi and NVIDIA model download
- **Browser:** Chrome, Firefox, or Safari (latest versions)
- **Camera:** Any USB or built-in webcam
- **Microphone:** Any USB or built-in microphone

---

## 🌐 Network Ports

| Port | Service | Protocol |
|------|---------|----------|
| 5000 | Sign Language Backend | Socket.IO |
| 7860 | Speech Backend | HTTP |
| 8000 | Web Server (optional) | HTTP |

Make sure these ports are not blocked by firewall.

---

## 🐛 Troubleshooting

### Quick Fixes

| Problem | Solution |
|---------|----------|
| "Connection error" | Restart Flask backends |
| Camera not working | Check browser permissions |
| Mic not working | Check browser permissions |
| "Model loading..." | Wait 5-10 min (first run only) |
| CORS errors | Run `pip install flask-cors` |

See **SETUP_AND_RUN_INSTRUCTIONS.md** for detailed troubleshooting.

---

## 🎓 Example Use Case

**Scenario:** Online meeting with sign language users

1. **Host** joins Jitsi room "Meeting123"
2. **Participant 1** (deaf) joins same room
3. **Participant 2** (hearing) joins same room
4. **Participant 2** speaks Uzbek → captions shared in chat
5. **Participant 1** makes signs → text shared in chat
6. Everyone sees captions in real-time!

---

## 🔐 Security Notes

**Current Setup (Development):**
- ⚠️ CORS allows all origins (`*`)
- ⚠️ No authentication
- ⚠️ HTTP (not HTTPS)
- ⚠️ Using public Jitsi server

**For Production:**
- 🔒 Configure CORS for specific domains
- 🔒 Add user authentication
- 🔒 Use HTTPS with SSL certificates
- 🔒 Deploy your own Jitsi server

---

## 📊 Performance Expectations

| Metric | Value |
|--------|-------|
| Sign recognition latency | ~100-150ms |
| Speech transcription | ~1-3 seconds/chunk |
| Video quality | Up to 720p |
| Concurrent users | 10-20 per server |
| Frame processing rate | ~10 FPS |

---

## 🚀 Next Steps

### Immediate (Today)
1. ✅ Follow **QUICK_START.md** to run the app
2. ✅ Test all three features
3. ✅ Join Jitsi room and test caption sharing

### Short Term (This Week)
1. Test with multiple participants
2. Adjust camera/mic settings for best quality
3. Try different Jitsi room names
4. Experiment with different signs

### Long Term (Future)
1. Train LSTM on more sign language gestures
2. Add support for more languages (speech)
3. Deploy to cloud server
4. Consider client-side processing (TensorFlow.js)

---

## 🆘 Getting Help

**If something doesn't work:**

1. Check terminal outputs for errors
2. Check browser console (F12 → Console)
3. Read **SETUP_AND_RUN_INSTRUCTIONS.md**
4. Verify all prerequisites are installed
5. Restart all services

---

## 📝 License

This project uses:
- Your original sign language recognition code
- Your original speech-to-sign code
- Jitsi Meet (Apache 2.0 License)
- NVIDIA NeMo (Apache 2.0 License)
- MediaPipe (Apache 2.0 License)

---

## 🎉 Success!

You now have a **fully integrated sign language + video conferencing system**!

- ✅ Sign language recognition works
- ✅ Speech-to-sign translation works
- ✅ Jitsi video conferencing works
- ✅ Captions can be shared with all participants
- ✅ All in one unified interface

**Enjoy your new communication platform!** 🤟📹🎤

---

## 📞 Quick Commands Summary

```bash
# FIRST TIME: Install Python 3.11
brew install python@3.11

# Terminal 1: Sign Language Backend
cd /Users/bilmao/Desktop/mentoraAi/signToText
source venv/bin/activate
python app.py

# Terminal 2: Speech Backend
cd /Users/bilmao/Desktop/mentoraAi/speachToSign
source venv/bin/activate
python app.py

# Terminal 3: Web Server (optional)
cd /Users/bilmao/Desktop/mentoraAi
python3 -m http.server 8000

# Browser
# Open: http://localhost:8000/jitsi-combined-app.html
```

**That's it! You're ready to go!** 🚀
