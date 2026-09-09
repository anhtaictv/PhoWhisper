import requests
import wave
import time

print("Creating 60-second WAV...")
with wave.open('large.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

file_size_mb = 1.83
print(f"File size: {file_size_mb}MB")
print("")
print("Uploading...")

start = time.time()
try:
    with open('large.wav', 'rb') as f:
        files = {'audio': ('large.wav', f)}
        resp = requests.post(
            'http://localhost:3000/transcribe',
            files=files,
            timeout=180
        )
    
    elapsed = time.time() - start
    print(f"Response: {resp.status_code} in {elapsed:.1f}s")
    print(f"Body: {resp.text}")
    
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.1f}s: {e}")
