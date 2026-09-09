import requests
import base64
import wave
import time

print("=== GATEWAY TRANSCRIBE TEST ===\n")

# Create 2-second test audio (silence)
print("[1] Creating test audio (2 seconds silence)...")
with wave.open('test.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 2))

with open('test.wav', 'rb') as f:
    audio_bytes = f.read()

print(f"    Audio: {len(audio_bytes)} bytes\n")

# Test via Gateway
print("[2] Sending to Gateway POST /transcribe...")
print("    URL: http://localhost:3000/transcribe")

start = time.time()
try:
    # Gateway expects multipart form data
    files = {'audio': ('test.wav', audio_bytes, 'audio/wav')}
    resp = requests.post(
        'http://localhost:3000/transcribe',
        files=files,
        timeout=120
    )
    elapsed = time.time() - start
    
    print(f"    Response: {resp.status_code}")
    print(f"    Time: {elapsed:.1f}s\n")
    
    if resp.status_code == 200:
        result = resp.json()
        print("[3] SUCCESS!")
        print(f"    Text: '{result.get('text', 'N/A')}'")
        print(f"    Model: {result.get('model', 'N/A')}")
    else:
        print(f"[3] ERROR")
        print(f"    Response: {resp.text[:500]}")
        
except requests.exceptions.Timeout as e:
    print(f"[3] TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"[3] ERROR: {e}")
