import requests
import wave
import time

with wave.open('test_60s.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

print("Uploading 60-second audio...")
start = time.time()

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
    print("✓ SUCCESS!")
    result = resp.json()
    print(f"  Model: {result['model']}")
    print(f"  Text: {result['text']}")
else:
    print(f"✗ Error: {resp.text}")
