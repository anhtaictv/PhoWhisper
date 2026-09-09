import requests
import json
import base64
import wave
import io
import time

# 1. Health check
print("[1] Health Check...")
resp = requests.get("http://localhost:8000/", timeout=5)
print(f"Status: {resp.status_code}")
print(f"Response: {resp.json()}\n")

# 2. List models
print("[2] Available Models...")
resp = requests.get("http://localhost:8000/api/tags", timeout=5)
models = resp.json()
for model in models.get("models", [])[:3]:
    print(f"  - {model['name']} ({model['size']})")
print()

# 3. Create a simple test audio (silence for quick testing)
print("[3] Creating test audio (silence, 1s)...")
sample_rate = 16000
duration_sec = 1
silence_data = b'\x00\x00' * (sample_rate * duration_sec)

# Pack as WAV
wav_buffer = io.BytesIO()
with wave.open(wav_buffer, 'wb') as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(silence_data)
wav_data = wav_buffer.getvalue()
audio_b64 = base64.b64encode(wav_data).decode()
print(f"OK - Audio created: {len(wav_data)} bytes\n")

# 4. Transcribe with LARGE model
print("[4] Transcribing with PhoWhisper-large...")
print("NOTE: First load may take 1-2 minutes (downloading 1.55GB model)...\n")

payload = {
    "audio": audio_b64,
    "model": "vinai/PhoWhisper-large"
}

start = time.time()
try:
    resp = requests.post("http://localhost:8000/api/transcribe", json=payload, timeout=180)
    elapsed = time.time() - start
    
    if resp.status_code == 200:
        result = resp.json()
        print(f"SUCCESS! ({elapsed:.1f}s)")
        print(f"Model: {result['model']}")
        print(f"Text: '{result['text']}'")
    else:
        print(f"ERROR: {resp.status_code}")
        print(f"Response: {resp.text}")
except requests.exceptions.Timeout:
    print(f"TIMEOUT after {elapsed:.1f}s (model likely still loading)")
except Exception as e:
    print(f"ERROR: {e}")

