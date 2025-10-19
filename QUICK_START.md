# ⚡ QUICK START GUIDE

## 📦 Installation (One-Time Setup)

**IMPORTANT:** You need Python 3.11 (MediaPipe doesn't support Python 3.13 yet)

### Step 0: Install Python 3.11 (if not installed)
```bash
# Install Python 3.11 using Homebrew
brew install python@3.11

# Verify installation
python3.11 --version
# Should show: Python 3.11.x
```

### Step 1: Create Virtual Environment for Sign Language
```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Verify Python version (should be 3.11.x)
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create Virtual Environment for Speech-to-Sign
```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign

# Create virtual environment with Python 3.11
python3.11 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Verify Python version (should be 3.11.x)
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the App (Every Time)

### Open 3 Terminal Windows:

**Terminal 1 - Sign Language Backend:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Run the server
python app.py
```
Wait for: `Running on http://0.0.0.0:5000`

---

**Terminal 2 - Speech Backend:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR on Windows: venv\Scripts\activate

# Run the server
python app.py
```
Wait for: `Running on http://0.0.0.0:7860`

---

**Terminal 3 - Web Server (Optional):**
```bash
cd /Users/bilmao/Desktop/mentoraAi
python3 -m http.server 8000
```

---

### Open Browser:
```
http://localhost:8000/jitsi-combined-app.html
```

Or directly: `file:///Users/bilmao/Desktop/mentoraAi/jitsi-combined-app.html`

---

## ✅ Success Checklist

- [ ] Terminal 1 shows "Running on http://0.0.0.0:5000"
- [ ] Terminal 2 shows "Running on http://0.0.0.0:7860"
- [ ] Browser opens the combined app
- [ ] Left panel: "✅ Connected to sign language server"
- [ ] Right panel: "✅ Speech server ready"

---

## 🎮 Usage

1. **Join Jitsi Room** (center panel) - Enter room name, click "Join Room"
2. **Sign Recognition** (left panel) - Click "Start Camera", make signs
3. **Speech Recognition** (right panel) - Click "Start Recording", speak Uzbek
4. **Share to Jitsi** - Click share buttons to send captions to chat

---

## 🛑 Stopping the App

1. Close browser tab
2. Press `Ctrl+C` in Terminal 1
3. Press `Ctrl+C` in Terminal 2
4. Press `Ctrl+C` in Terminal 3 (if used)

---

## 🆘 Troubleshooting

**Problem:** Connection errors
**Solution:** Restart both Flask backends (Terminal 1 & 2)

**Problem:** Camera/mic not working
**Solution:** Check browser permissions, refresh page

**Problem:** Model loading...
**Solution:** Wait 5-10 minutes for NVIDIA model download (first run only)

---

For detailed instructions, see: `SETUP_AND_RUN_INSTRUCTIONS.md`
