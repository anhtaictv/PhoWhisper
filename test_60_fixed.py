import requests
import wave
import base64
import time

# Create 60s audio
print("[1] Creating 60-second audio...")
with wave.open('test_60_new.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

print("[2] Testing PhoWhisper server directly...")
with open('test_60_new.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

start = time.time()
resp = requests.post(
    'http://localhost:8000/api/transcribe',
    json={'audio': audio_b64},
    timeout=180
)
elapsed = time.time() - start

print(f"    Status: {resp.status_code} ({elapsed:.1f}s)")

if resp.status_code == 200:
    print("    ✓ PhoWhisper accepts 60s!")
    data = resp.json()
    print(f"    Text: {data['text'][:80]}")
else:
    print(f"    ✗ Error: {resp.text[:200]}")

print("")
print("[3] Testing Gateway...")
with open('test_60_new.wav', 'rb') as f:
    files = {'audio': ('test.wav', f)}
    start = time.time()
    resp = requests.post(
        'http://localhost:3000/transcribe',
        files=files,
        timeout=180
    )
    elapsed = time.time() - start

print(f"    Status: {resp.status_code} ({elapsed:.1f}s)")

if resp.status_code == 200:
    print("    ✓ Gateway accepts 60s!")
    data = resp.json()
    print(f"    Model: {data['model']}")
else:
    print(f"    ✗ Error: {resp.text[:100]}")
