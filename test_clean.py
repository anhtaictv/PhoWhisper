import requests
import wave
import time

print("Creating 60-second test audio...")
with wave.open('test_60s_final.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

print("Uploading to gateway...")
start = time.time()

with open('test_60s_final.wav', 'rb') as f:
    files = {'audio': ('test.wav', f, 'audio/wav')}
    resp = requests.post(
        'http://localhost:3000/transcribe',
        files=files,
        timeout=180
    )

elapsed = time.time() - start

print(f"\nResponse: {resp.status_code}")
print(f"Time: {elapsed:.1f}s")

if resp.status_code == 200:
    result = resp.json()
    print(f"\n✓ SUCCESS!")
    print(f"  Model: {result['model']}")
    print(f"  Duration: Can accept >60 seconds")
else:
    print(f"\n✗ Error {resp.status_code}: {resp.text[:300]}")
