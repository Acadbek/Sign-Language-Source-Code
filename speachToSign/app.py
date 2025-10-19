"""
Uzbek Speech Recognition with NVIDIA FastConformer
Client-side audio recording, server-side transcription
Optimized for Hugging Face Spaces deployment
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import nemo.collections.asr as nemo_asr
import tempfile
import os
import threading
import librosa
import soundfile as sf

app = Flask(__name__)
CORS(app)  # Enable CORS for WebGL Unity builds

print("=" * 60)
print("🔄 Loading NVIDIA FastConformer for Uzbek...")
print("=" * 60)

asr_model = None
model_loaded = False

last_transcribed_text = ""
last_animation_data = []
last_transcription_lock = threading.Lock()

# Available letters in Unity
AVAILABLE_LETTERS = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
    'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'
]


def load_nvidia_model():
    """Load NeMo ASR model in background thread"""
    global asr_model, model_loaded
    try:
        print("📥 Loading nvidia/stt_uz_fastconformer_hybrid_large_pc...")
        asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
            model_name="nvidia/stt_uz_fastconformer_hybrid_large_pc"
        )
        model_loaded = True
        print("✅ NVIDIA FastConformer loaded successfully!")
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        model_loaded = False


# Start model loading in background
model_thread = threading.Thread(target=load_nvidia_model, daemon=True)
model_thread.start()


def process_text_to_letters(text):
    """
    Convert text to fingerspelling
    Each word shown letter by letter
    """
    words = text.lower().split()
    animation_data = []

    for word in words:
        if not word:
            continue

        # Clean word - keep only available letters
        clean_word = ''.join(c for c in word if c.isalnum() and c in AVAILABLE_LETTERS)

        if not clean_word:
            continue

        letters = list(clean_word)

        if letters:
            animation_data.append({
                "type": "letters",
                "word": clean_word,
                "letters": letters
            })
            print(f"🔤 Word '{clean_word}' → Fingerspelling: {' '.join(letters).upper()}")

    return animation_data


def transcribe_uzbek_audio(audio_path):
    """Transcribe audio file using NeMo model"""
    global asr_model

    try:
        # Ensure audio is in correct format (16kHz mono)
        audio, sr = librosa.load(audio_path, sr=16000, mono=True)

        # Проверка длины аудио
        duration = len(audio) / sr
        print(f"📊 Audio duration: {duration:.2f} seconds")

        if duration < 0.3:
            print("⚠️ Audio too short!")
            return ""

        # Save as temporary WAV file
        temp_wav = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        sf.write(temp_wav.name, audio, 16000)

        # Transcribe
        outputs = asr_model.transcribe([temp_wav.name])

        # Clean up temp file
        try:
            os.unlink(temp_wav.name)
        except:
            pass

        if outputs and len(outputs) > 0:
            result = outputs[0]

            # ===== ИСПРАВЛЕНИЕ: Извлекаем текст правильно =====
            if hasattr(result, 'text'):
                # Если это объект Hypothesis
                text = result.text
            elif isinstance(result, str):
                # Если это уже строка
                text = result
            elif isinstance(result, list):
                # Если это список
                text = " ".join(str(item) for item in result)
            else:
                # Попытка конвертировать в строку
                text = str(result)

            # Очистка текста от мусора
            text = text.strip()

            # Дебаг информация
            print(f"🔍 Result type: {type(result)}")
            print(f"🔍 Result attributes: {dir(result) if hasattr(result, '__dict__') else 'N/A'}")
            print(f"📝 Extracted text: '{text}'")

            if not text:
                print("⚠️ Empty transcription result")
                return ""

            return text

    except Exception as e:
        print(f"❌ Transcription error: {e}")
        import traceback
        traceback.print_exc()
        return ""

    return ""


@app.route('/')
def index():
    """Serve main web interface"""
    return render_template('ind.html')


@app.route('/message', methods=['GET'])
def get_message():
    """Unity endpoint - send fingerspelling sequence"""
    global last_animation_data

    with last_transcription_lock:
        # Create letter sequence for Unity
        letter_sequence = []

        for item in last_animation_data:
            if item["type"] == "letters":
                for letter in item["letters"]:
                    letter_sequence.append(f"letter_{letter}")

        message_string = " ".join(letter_sequence)

        print(f"📤 Sending to Unity: {message_string}")

        return jsonify({
            "message": message_string,
            "animation_data": last_animation_data,
            "language": "uz"
        })


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """
    Receive audio from browser, transcribe, return fingerspelling data
    Expects audio file in FormData with key 'audio'
    """
    global model_loaded, last_transcribed_text, last_animation_data

    if not model_loaded:
        return jsonify({
            "success": False,
            "error": "Model is still loading... Please wait."
        }), 503

    try:
        # Check if audio file was sent
        if 'audio' not in request.files:
            return jsonify({
                "success": False,
                "error": "No audio file received"
            }), 400

        audio_file = request.files['audio']

        if audio_file.filename == '':
            return jsonify({
                "success": False,
                "error": "Empty audio file"
            }), 400

        print(f"📁 Received audio file: {audio_file.filename}")

        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
            audio_file.save(tmp_path)

        print("🎙️ Transcribing audio...")

        # Transcribe
        uzbek_text = transcribe_uzbek_audio(tmp_path)

        # Clean up temp file
        try:
            os.unlink(tmp_path)
        except:
            pass

        if uzbek_text:
            print(f"✅ Transcribed: {uzbek_text}")

            # Convert to fingerspelling
            animation_data = process_text_to_letters(uzbek_text)

            # Save for Unity endpoint
            with last_transcription_lock:
                last_transcribed_text = uzbek_text
                last_animation_data = animation_data

            return jsonify({
                "success": True,
                "uzbek": uzbek_text,
                "animation_data": animation_data,
                "language": "uz",
                "model": "NVIDIA FastConformer"
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not transcribe audio. Please speak clearly."
            }), 400

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "error": f"Server error: {str(e)}"
        }), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "model_loaded": model_loaded,
        "model": "NVIDIA FastConformer (uz)" if model_loaded else "loading...",
        "wer": "16.46%" if model_loaded else "N/A",
        "mode": "Client-side Recording + Server-side Transcription"
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 NVIDIA FastConformer - Fingerspelling Server")
    print("=" * 60)
    print("📱 Interface: http://0.0.0.0:7860")
    print("🎯 WER: 16.46%")
    print("🔤 MODE: Client-side recording")
    print("🎮 Unity endpoint: /message")
    print("=" * 60)

    # Hugging Face Spaces uses port 7860
    app.run(host='0.0.0.0', port=7860, debug=False)