# ⚠️ Python Version Compatibility Issue

## 🔴 Problem

If you see this error:
```
ERROR: Could not find a version that satisfies the requirement mediapipe>=0.10.0
```

**Cause:** You're using Python 3.13, which is too new for MediaPipe.

---

## ✅ Solution: Use Python 3.11

### Step 1: Install Python 3.11

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Verify installation
python3.11 --version
# Should show: Python 3.11.x
```

---

### Step 2: Delete Old Virtual Environments

```bash
# Delete sign language venv
cd /Users/bilmao/Desktop/mentoraAi/signToText
rm -rf venv

# Delete speech venv
cd /Users/bilmao/Desktop/mentoraAi/speachToSign
rm -rf venv
```

---

### Step 3: Recreate with Python 3.11

**For Sign Language:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/signToText

# Create venv with Python 3.11
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify version (MUST show 3.11.x)
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

**For Speech-to-Sign:**
```bash
cd /Users/bilmao/Desktop/mentoraAi/speachToSign

# Create venv with Python 3.11
python3.11 -m venv venv

# Activate
source venv/bin/activate

# Verify version (MUST show 3.11.x)
python --version

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

---

## 📊 Python Version Compatibility

| Python Version | MediaPipe | TensorFlow | NeMo | Status |
|----------------|-----------|------------|------|--------|
| 3.13 | ❌ | ✅ | ❌ | **NOT SUPPORTED** |
| 3.12 | ✅ | ✅ | ⚠️ | Works (some warnings) |
| 3.11 | ✅ | ✅ | ✅ | **RECOMMENDED** ⭐ |
| 3.10 | ✅ | ✅ | ✅ | Works |
| 3.9 | ✅ | ✅ | ✅ | Works |
| 3.8 | ⚠️ | ✅ | ✅ | Older, not recommended |

**Recommendation:** Use Python 3.11 for best compatibility.

---

## 🔍 How to Check Your Python Version

```bash
# Check system Python version
python3 --version

# Check Python 3.11 specifically
python3.11 --version

# Inside virtual environment
source venv/bin/activate
python --version
```

---

## 💡 Why Python 3.11?

- ✅ **Fully compatible** with all dependencies
- ✅ **Stable and tested** - production-ready
- ✅ **Fast** - performance improvements over 3.10
- ✅ **Supported** by MediaPipe, TensorFlow, and NeMo
- ✅ **Not too old** - still maintained by Python core team

---

## 🆘 Troubleshooting

### "python3.11: command not found"

**Solution:**
```bash
# Install Python 3.11
brew install python@3.11

# If still not found, add to PATH
export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"
```

### "Permission denied"

**Solution:**
```bash
# Don't use sudo with virtual environments!
# Just use regular pip install
pip install -r requirements.txt
```

### "Package conflicts"

**Solution:**
```bash
# Delete and recreate venv
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

## ✅ Verification

After installation, verify everything:

```bash
# Activate venv
source venv/bin/activate

# Check Python version (should be 3.11.x)
python --version

# Check packages are installed
pip list | grep -E "mediapipe|tensorflow|flask"

# Should show:
# flask                3.x.x
# mediapipe           0.10.x
# tensorflow          2.x.x
```

---

**If you followed these steps, everything should work!** 🚀
