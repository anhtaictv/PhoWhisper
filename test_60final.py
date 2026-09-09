import requests, wave, time

print('[1] Creating 60-second audio...')
with wave.open('final60.wav', 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(16000)
    w.writeframes(b'\x00\x00' * (16000 * 60))

print('[2] Uploading to gateway...')
start = time.time()
with open('final60.wav', 'rb') as f:
    r = requests.post('http://localhost:3000/transcribe', files={'audio': ('test.wav', f)}, timeout=180)
elapsed = time.time() - start

print(f'[3] Response: {r.status_code} ({elapsed:.1f}s)')
if r.status_code == 200:
    print('SUCCESS! 60-second audio WORKS!')
    d = r.json()
    print(f'Model: {d["model"]}')
else:
    print(f'Error: {r.text[:150]}')
