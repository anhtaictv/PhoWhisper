import requests, wave, base64, time

print("Testing PhoWhisper server directly with 60s audio...")

with wave.open("test_60.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(b"\x00\x00" * (16000 * 60))

with open("test_60.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

print(f"Audio size: {len(audio_b64) / 1024 / 1024:.2f}MB")

start = time.time()
r = requests.post(
    "http://localhost:8000/api/transcribe",
    json={"audio": audio_b64},
    timeout=180
)
elapsed = time.time() - start

print(f"Status: {r.status_code} ({elapsed:.1f}s)")
print(f"Response: {r.text}")
