import requests
import wave
import base64
import time

with wave.open('t60.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

print("Sending 60-second audio to gateway...")
with open('t60.wav', 'rb') as f:
    files = {'audio': ('test.wav', f)}
    start = time.time()
    resp = requests.post(
        'http://localhost:3000/transcribe',
        files=files,
        timeout=180
    )
    elapsed = time.time() - start

print(f"Response: {resp.status_code} ({elapsed:.1f}s)")

if resp.status_code == 200:
    print("✓ SUCCESS - 60-second audio works!")
    data = resp.json()
    print(f"  Text: {data['text'][:100]}")
else:
    print(f"✗ Error: {resp.text}")
