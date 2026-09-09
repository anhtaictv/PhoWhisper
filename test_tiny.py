import requests
import wave
import json

print("1. Creating 1-second WAV file...")
with wave.open('tiny.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(16000)
    wav.writeframes(b'\x00\x00' * 16000)

print("2. Sending to gateway /transcribe...")
with open('tiny.wav', 'rb') as f:
    files = {'audio': ('tiny.wav', f, 'audio/wav')}
    
    # First, test file can be sent
    resp = requests.post(
        'http://localhost:3000/health',
        timeout=5
    )
    print(f"   Health: {resp.status_code}")
    
    # Now test /transcribe
    resp = requests.post(
        'http://localhost:3000/transcribe',
        files=files,
        timeout=60
    )
    
    print(f"3. Response: {resp.status_code}")
    print(f"   Body: {resp.text}")
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"\n✓ SUCCESS!")
        print(f"   Text: {data.get('text', 'N/A')}")
