import requests
import wave
import base64
import time

# Create 60s audio
print("[1] Creating 60-second audio file...")
with wave.open('test_60s.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

with open('test_60s.wav', 'rb') as f:
    file_size = len(f.read())

print(f"    File: {file_size / 1024 / 1024:.2f}MB")
print("")

# Test upload
print("[2] Uploading to gateway (may take 2-3 minutes)...")
start = time.time()

try:
    with open('test_60s.wav', 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        resp = requests.post(
            'http://localhost:3000/transcribe',
            files=files,
            timeout=180
        )
    
    elapsed = time.time() - start
    
    print(f"    Status: {resp.status_code}")
    print(f"    Time: {elapsed:.1f}s")
    print("")
    
    if resp.status_code == 200:
        print("[3] SUCCESS!")
        result = resp.json()
        print(f"    Text: '{result.get('text', 'N/A')}'")
        print(f"    Model: {result.get('model', 'N/A')}")
    else:
        print(f"[3] ERROR: {resp.status_code}")
        print(f"    Message: {resp.text[:300]}")
        
except requests.exceptions.Timeout:
    print(f"[3] TIMEOUT after {elapsed:.1f}s")
except Exception as e:
    print(f"[3] ERROR: {e}")
