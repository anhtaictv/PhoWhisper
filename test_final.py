import requests
import wave
import base64
import time

# Create 60s audio
with wave.open('test_60s.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

print("[Test] Uploading 60-second audio...")
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
    print(f"Status: {resp.status_code} ({elapsed:.1f}s)")
    
    if resp.status_code == 200:
        print("✓ SUCCESS - 60s audio accepted!")
        result = resp.json()
        print(f"  Model: {result['model']}")
        print(f"  Text: {result['text'][:100]}")
    else:
        print(f"✗ Error: {resp.text[:200]}")
        
except Exception as e:
    print(f"✗ Failed: {e}")
