import requests
import base64
import wave
import time

# Create simple test audio
with wave.open('test.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * 16000)

with open('test.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

print("[Testing PhoWhisper directly]")
print(f"Audio: {len(audio_b64)} bytes")

try:
    start = time.time()
    resp = requests.post(
        'http://localhost:8000/api/transcribe',
        json={'audio': audio_b64, 'model': 'vinai/PhoWhisper-small'},
        timeout=120
    )
    elapsed = time.time() - start
    
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        result = resp.json()
        print(f"Result: {result}")
        print(f"Time: {elapsed:.1f}s")
    else:
        print(f"Error: {resp.text}")
        
except requests.exceptions.Timeout:
    print(f"TIMEOUT after {time.time() - start:.1f}s")
except Exception as e:
    print(f"Error: {e}")
