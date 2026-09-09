import requests
import json

print("[1] Health check...")
try:
    resp = requests.get('http://localhost:8000/', timeout=5)
    print(f"    Status: {resp.status_code}")
    print(f"    Response: {resp.json()}")
except Exception as e:
    print(f"    Error: {e}")

print("")
print("[2] List models...")
try:
    resp = requests.get('http://localhost:8000/api/tags', timeout=5)
    data = resp.json()
    print(f"    Models: {len(data['models'])} available")
except Exception as e:
    print(f"    Error: {e}")

print("")
print("[3] Test transcribe (small audio)...")
import wave
import base64
import time

# Create 1-second audio
with wave.open('test_1s.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * 16000)

with open('test_1s.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

start = time.time()
try:
    resp = requests.post(
        'http://localhost:8000/api/transcribe',
        json={'audio': audio_b64},
        timeout=60
    )
    elapsed = time.time() - start
    print(f"    Status: {resp.status_code} ({elapsed:.1f}s)")
    if resp.status_code == 200:
        print(f"    Result: {resp.json()}")
    else:
        print(f"    Error: {resp.text[:200]}")
except Exception as e:
    print(f"    Error: {e}")
