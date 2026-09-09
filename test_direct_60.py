import requests
import wave
import base64
import time

print("Testing PhoWhisper server with 60-second audio...")
print("")

# Create 60s audio
with wave.open('test_60_direct.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

with open('test_60_direct.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

print(f"Audio B64 size: {len(audio_b64) / 1024 / 1024:.2f}MB")
print("")
print("Sending to PhoWhisper directly...")

start = time.time()
try:
    resp = requests.post(
        'http://localhost:8000/api/transcribe',
        json={'audio': audio_b64},
        timeout=180
    )
    
    elapsed = time.time() - start
    print(f"Response: {resp.status_code} in {elapsed:.1f}s")
    
    if resp.status_code == 200:
        print("✓ PhoWhisper accepts 60s audio!")
        data = resp.json()
        print(f"  Text: {data['text']}")
    else:
        print(f"✗ Error: {resp.text[:300]}")
        
except Exception as e:
    elapsed = time.time() - start
    print(f"✗ Error after {elapsed:.1f}s: {e}")
