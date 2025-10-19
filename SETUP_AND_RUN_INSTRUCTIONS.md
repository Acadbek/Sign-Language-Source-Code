# 🚀 Sign Language + Jitsi Integration - Setup & Run Instructions

Complete step-by-step guide to run the integrated application.

---

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Python 3.11** installed (3.12 also works, 3.13 does NOT work with MediaPipe)
- ✅ pip (Python package manager)
- ✅ Homebrew (for macOS - to install Python 3.11)
- ✅ Webcam and microphone
- ✅ Modern web browser (Chrome, Firefox, or Safari)
- ✅ Stable internet connection

### Install Python 3.11

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version
# Should output: Python 3.11.x
```

---

## 🔧 Step 1: Install Python Dependencies

**IMPORTANT:** Use virtual environments to avoid dependency conflicts!

**CRITICAL:** Must use Python 3.11 (MediaPipe doesn't support Python 3.13)

### For Sign Language Recognition (signToText)

```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# You should see (venv) in your terminal prompt

# Verify Python version (MUST be 3.11.x)
python --version

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install from requirements.txt
pip install -r requirements.txt
```

### For Speech-to-Sign (speachToSign)

```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# You should see (venv) in your terminal prompt

# Verify Python version (MUST be 3.11.x)
python --version

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install from requirements.txt
pip install -r requirements.txt
```

**Note:** NVIDIA NeMo installation may take 5-10 minutes. It's a large package.

### Why Virtual Environments?

✅ **Isolates dependencies** - No conflicts with other projects
✅ **Clean installation** - Easy to delete and recreate
✅ **Reproducible** - Same versions every time
✅ **Best practice** - Professional Python development

### Why Python 3.11?

⚠️ **Python 3.13 is too new** - MediaPipe doesn't support it yet
✅ **Python 3.11** - Fully compatible with all dependencies
✅ **Python 3.12** - Also works (but 3.11 is more tested)

---

## 📂 Step 2: Verify Model Files

Make sure these files exist:

### Sign Language Models
```bash
ls /Users/bilmao/Desktop/mentoraAi/signToText/
```

Should show:
- ✅ `actions_holistic.keras` (5.7 MB)
- ✅ `actions_holistic_actions.npy`

### Speech Model
The NVIDIA NeMo model will download automatically on first run (~500 MB).

---

## 🎯 Step 3: Start the Flask Backends

You need to run **TWO Flask servers** in **separate terminal windows**.

### Terminal 1: Start Sign Language Backend

```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText

# Activate virtual environment FIRST!
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# You should see (venv) in your prompt

# Now run the server
python app.py
```

**Expected output:**
```
Loading model...
Model loaded! Actions: [array of actions]
Starting Flask-SocketIO server...
Model: X actions, Y frames
Using: Z frames for prediction
 * Running on http://0.0.0.0:5000
```

✅ **Leave this terminal running!** The server must stay active.

---

### Terminal 2: Start Speech-to-Sign Backend

```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign

# Activate virtual environment FIRST!
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# You should see (venv) in your prompt

# Now run the server
python app.py
```

**Expected output:**
```
============================================================
🔄 Loading NVIDIA FastConformer for Uzbek...
============================================================
📥 Loading nvidia/stt_uz_fastconformer_hybrid_large_pc...
✅ NVIDIA FastConformer loaded successfully!
============================================================
🚀 NVIDIA FastConformer - Fingerspelling Server
============================================================
📱 Interface: http://0.0.0.0:7860
🎯 WER: 16.46%
🔤 MODE: Client-side recording
🎮 Unity endpoint: /message
============================================================
 * Running on http://0.0.0.0:7860
```

**Note:** First run will download the NVIDIA model (~500 MB). This may take a few minutes.

✅ **Leave this terminal running too!**

---

## 🌐 Step 4: Open the Web Application

### Option 1: Direct File Open (Easiest)

1. Open your web browser
2. Go to: `file:///Users/bilmao/Desktop/mentoraAi/jitsi-combined-app.html`
3. Or double-click the `jitsi-combined-app.html` file

### Option 2: Use HTTP Server (Recommended)

```bash
# Open a THIRD terminal
cd /Users/bilmao/Desktop/mentoraAi
python3 -m http.server 8000
```

Then open browser to: `http://localhost:8000/jitsi-combined-app.html`

---

## 🎮 Step 5: Using the Application

### Sign Language Recognition (Left Panel)

1. **Start Camera**: Click "▶️ Start Camera"
2. **Allow camera access** when browser prompts
3. **Make hand signs** in front of the camera
4. Recognized words appear in the purple box
5. **Share to Jitsi**: Click "📤 Share to Jitsi" to send to chat

### Jitsi Video Conference (Center Panel)

1. **Enter room name** (e.g., "SignLanguageRoom")
2. **Click "Join Room"**
3. **Allow camera/mic access** when Jitsi prompts
4. **Share room name** with others to join
5. Captions from sign/speech will appear in Jitsi chat

### Speech-to-Sign (Right Panel)

1. **Start Recording**: Click "🎤 Start Recording"
2. **Allow microphone access** when browser prompts
3. **Speak in Uzbek** (the app records in 3-second chunks)
4. Transcription appears in green box
5. Fingerspelling letters appear below
6. **Share to Jitsi**: Click "📤 Share to Jitsi" to send to chat

---

## 🔍 Verification Checklist

Before using, verify all components are working:

### Check 1: Sign Language Backend
```bash
# In browser, go to:
http://localhost:5000/

# Should show the original sign language interface
```

### Check 2: Speech Backend
```bash
# In browser, go to:
http://localhost:7860/health

# Should return JSON:
{
  "status": "running",
  "model_loaded": true,
  "model": "NVIDIA FastConformer (uz)",
  "wer": "16.46%"
}
```

### Check 3: Combined App
```bash
# Open:
file:///Users/bilmao/Desktop/mentoraAi/jitsi-combined-app.html

# Check status indicators:
# - Sign panel: "✅ Connected to sign language server"
# - Speech panel: "✅ Speech server ready"
```

---

## 🐛 Troubleshooting

### Problem: "Connection error. Is Flask running on port 5000?"

**Solution:**
1. Check if signToText backend is running
2. Verify no other app is using port 5000:
   ```bash
   lsof -i :5000
   ```
3. Restart the signToText backend

---

### Problem: "Server unavailable. Is Flask running on port 7860?"

**Solution:**
1. Check if speachToSign backend is running
2. Verify NVIDIA NeMo model loaded successfully
3. Check terminal for error messages
4. Restart the speachToSign backend

---

### Problem: Camera not working

**Solution:**
1. Check browser permissions (Chrome: Settings → Privacy → Camera)
2. Make sure no other app is using the camera
3. Try refreshing the page
4. Try a different browser

---

### Problem: Microphone not working

**Solution:**
1. Check browser permissions (Chrome: Settings → Privacy → Microphone)
2. Make sure microphone is not muted in system settings
3. Try refreshing the page

---

### Problem: "Model loading..." never completes

**Solution:**
1. Check your internet connection (NVIDIA model downloads on first run)
2. Wait 5-10 minutes for initial download
3. Check terminal for errors
4. If download fails, try running again:
   ```bash
   cd /Users/bilmao/Desktop/mentoraAi/speachToSign
   python app.py
   ```

---

### Problem: Jitsi won't load

**Solution:**
1. Check your internet connection
2. Try different room name
3. Clear browser cache
4. Try incognito/private browsing mode

---

### Problem: CORS errors in browser console

**Solution:**
This should be fixed with flask-cors. If errors persist:

1. Verify flask-cors is installed:
   ```bash
   pip install flask-cors
   ```

2. Check that both backends have CORS enabled in code

3. Restart both Flask backends

---

## 📊 Port Summary

Make sure these ports are available:

| Service | Port | Purpose |
|---------|------|---------|
| Sign Language Backend | 5000 | Socket.IO for video processing |
| Speech Backend | 7860 | HTTP for audio transcription |
| Optional HTTP Server | 8000 | Serving HTML file |

---

## 🎓 Quick Start Commands (All-in-One)

### Terminal 1:
```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText && python app.py
```

### Terminal 2:
```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign && python app.py
```

### Terminal 3 (Optional):
```bash
cd /Users/bilmao/Desktop/mentoraAi && python3 -m http.server 8000
```

### Browser:
```
http://localhost:8000/jitsi-combined-app.html
```

---

## 🎯 Expected Workflow

1. **Start both Flask backends** (Terminal 1 & 2)
2. **Open combined app** in browser
3. **Join Jitsi room** (center panel)
4. **Start sign recognition** (left panel)
5. **Start speech recording** (right panel)
6. **Share captions to Jitsi** using share buttons
7. **All participants see captions** in Jitsi chat

---

## 💡 Tips for Best Performance

1. **Camera**: Use good lighting for better sign recognition
2. **Microphone**: Speak clearly in Uzbek for better transcription
3. **Internet**: Stable connection required for Jitsi
4. **Browser**: Chrome or Firefox recommended
5. **CPU**: Sign recognition is CPU-intensive, close other apps if slow

---

## 📱 Testing with Multiple Participants

1. **Person 1**: Opens the combined app, joins room "TestRoom"
2. **Person 2**: Opens the combined app, joins room "TestRoom"
3. Both can see each other in Jitsi
4. Person 1 makes signs → clicks "Share to Jitsi"
5. Person 2 sees caption in Jitsi chat
6. Person 2 speaks Uzbek → clicks "Share to Jitsi"
7. Person 1 sees caption in Jitsi chat

---

## 🔐 Security Notes

- The app runs locally on your machine
- Video processing happens on your local Flask server
- Jitsi uses meet.jit.si (public server)
- For production, use your own Jitsi server
- Never commit sensitive data to version control

---

## 🆘 Getting Help

If you encounter issues:

1. **Check terminal outputs** for error messages
2. **Check browser console** (F12 → Console tab)
3. **Verify all prerequisites** are installed
4. **Try restarting** all services
5. **Check firewall settings** (ports 5000, 7860, 8000)

---

## ✅ Success Indicators

Everything is working if you see:

- ✅ Terminal 1: "Running on http://0.0.0.0:5000"
- ✅ Terminal 2: "Running on http://0.0.0.0:7860"
- ✅ Browser: All status indicators show green/connected
- ✅ Sign panel: Video feed appears when camera starts
- ✅ Speech panel: Transcriptions appear when speaking
- ✅ Jitsi: Video conference loads and connects

---

## 🎉 You're All Set!

Your integrated Sign Language + Jitsi application is now running!

**Enjoy real-time sign language recognition and speech-to-sign translation in your video conferences!** 🤟📹🎤
