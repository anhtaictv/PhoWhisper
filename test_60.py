import requests, wave, time

print("Creating 60-second test audio...")
with wave.open("test_60.wav", "wb") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(b"\x00\x00" * (16000 * 60))

print("Testing gateway with 60-second audio...")
start = time.time()
with open("test_60.wav", "rb") as f:
    r = requests.post(
        "http://localhost:3000/transcribe",
        files={"audio": ("test.wav", f)},
        timeout=180
    )
elapsed = time.time() - start

print(f"Status: {r.status_code}")
print(f"Time: {elapsed:.1f}s")

if r.status_code == 200:
    print("✅ SUCCESS! 60-second audio WORKS!")
    d = r.json()
    print(f"Model: {d.get('model', 'N/A')}")
    print(f"Text: {d.get('text', 'N/A')[:80]}")
else:
    print(f"❌ Error: {r.text[:300]}")
