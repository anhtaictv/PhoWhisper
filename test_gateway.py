import wave
import base64
import json
import requests

# Create test WAV (1 second silence at 16kHz)
sample_rate = 16000
duration = 1
silence = b'\x00\x00' * (sample_rate * duration)

# Write WAV
with wave.open('test_audio.wav', 'wb') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    wav.writeframes(silence)

# Read and encode
with open('test_audio.wav', 'rb') as f:
    audio_b64 = base64.b64encode(f.read()).decode()

print(f"Audio size: {len(audio_b64)} bytes")

# Test transcribe
try:
    response = requests.post(
        'http://localhost:3000/transcribe',
        data={'audio': open('test_audio.wav', 'rb')},
        timeout=60,
        files={'audio': open('test_audio.wav', 'rb')}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error: {e}")
