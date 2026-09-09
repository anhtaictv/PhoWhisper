import requests
import wave
import base64

# Create 1 minute audio file (should exceed old 30s limit)
print("[Testing] Creating 60-second audio file...")
with wave.open('test_60s.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * (16000 * 60))

with open('test_60s.wav', 'rb') as f:
    file_size = len(f.read())

print(f"File size: {file_size / 1024 / 1024:.2f}MB (60 seconds of silence)")

# Test upload
print("[Testing] Uploading to gateway...")
try:
    with open('test_60s.wav', 'rb') as f:
        files = {'audio': ('test.wav', f, 'audio/wav')}
        resp = requests.post(
            'http://localhost:3000/transcribe',
            files=files,
            timeout=120
        )
    
    print(f"Response: {resp.status_code}")
    if resp.status_code == 200:
        print(f"✓ SUCCESS - 60s audio accepted!")
        result = resp.json()
        print(f"  Text: {result.get('text', 'N/A')[:100]}")
    else:
        print(f"Error: {resp.text[:200]}")
except Exception as e:
    print(f"Error: {e}")
