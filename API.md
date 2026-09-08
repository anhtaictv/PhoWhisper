# PhoWhisper API (Ollama-style)

Simple REST API để gọi Vietnamese speech recognition từ AI Gateway.

## Server URL

```
http://phowhisper-server.tailxxxx.ts.net:8000
```

## Endpoints

### 1. Health Check

```bash
curl http://localhost:8000/
```

Response:
```json
{
  "name": "PhoWhisper",
  "version": "1.0.0"
}
```

### 2. Transcribe Audio

**POST** `/api/transcribe`

Request:
```json
{
  "audio": "base64_encoded_audio_data",
  "model": "vinai/PhoWhisper-small"
}
```

Response:
```json
{
  "text": "Xin chào thế giới",
  "model": "vinai/PhoWhisper-small"
}
```

**Example (Python):**
```python
import requests
import base64

with open("audio.wav", "rb") as f:
    audio_b64 = base64.b64encode(f.read()).decode()

response = requests.post(
    "http://localhost:8000/api/transcribe",
    json={
        "audio": audio_b64,
        "model": "vinai/PhoWhisper-small"
    }
)

print(response.json()["text"])
```

**Example (cURL):**
```bash
# Encode audio
AUDIO=$(base64 -w0 audio.wav)

# Send request
curl -X POST http://localhost:8000/api/transcribe \
  -H "Content-Type: application/json" \
  -d "{\"audio\":\"$AUDIO\",\"model\":\"vinai/PhoWhisper-small\"}"
```

**Example (Node.js):**
```javascript
const fs = require('fs');
const axios = require('axios');

const audio = fs.readFileSync('audio.wav').toString('base64');

axios.post('http://localhost:8000/api/transcribe', {
  audio: audio,
  model: 'vinai/PhoWhisper-small'
}).then(res => {
  console.log(res.data.text);
});
```

### 3. List Models

**GET** `/api/tags`

Response:
```json
{
  "models": [
    {"name": "vinai/PhoWhisper-tiny", "size": "39M"},
    {"name": "vinai/PhoWhisper-base", "size": "74M"},
    {"name": "vinai/PhoWhisper-small", "size": "244M"},
    {"name": "vinai/PhoWhisper-medium", "size": "769M"},
    {"name": "vinai/PhoWhisper-large", "size": "1.55B"}
  ]
}
```

## Models

| Model | Size | Speed | Notes |
|-------|------|-------|-------|
| vinai/PhoWhisper-tiny | 39M | ⚡⚡⚡ | Fastest, lower accuracy |
| vinai/PhoWhisper-base | 74M | ⚡⚡ | - |
| vinai/PhoWhisper-small | 244M | ⚡ | Recommended |
| vinai/PhoWhisper-medium | 769M | - | Better accuracy |
| vinai/PhoWhisper-large | 1.55B | - | Best accuracy |

## Integration Examples

### AI Gateway → PhoWhisper

```python
from client import PhoWhisperClient

# Connect via Tailscale
client = PhoWhisperClient(
    server_url="http://phowhisper-server.tailxxxx.ts.net:8000"
)

# Transcribe
text = client.transcribe("/path/to/audio.wav")
```

### Direct HTTP

```python
import requests
import base64

def transcribe(audio_path, server="http://phowhisper-server.tailxxxx.ts.net:8000"):
    with open(audio_path, 'rb') as f:
        audio_b64 = base64.b64encode(f.read()).decode()
    
    resp = requests.post(f"{server}/api/transcribe", json={
        "audio": audio_b64,
        "model": "vinai/PhoWhisper-small"
    })
    return resp.json()["text"]
```

## Timeouts

Transcription time depends on model:
- **tiny**: 500ms - 1s per minute of audio
- **small**: 2-5s per minute
- **large**: 10-20s per minute

Set request timeout accordingly:
```python
requests.post(..., timeout=300)  # 5 minutes
```

## Error Handling

```json
{
  "detail": "Missing 'audio' field"
}
```

Common errors:
- 400: Missing audio field or bad format
- 500: Model loading or transcription error

## Performance Tips

1. Use **smaller model** (tiny, base) for speed
2. Use **larger model** (medium, large) for accuracy
3. Enable GPU if available: set `USE_GPU=1`
4. Batch transcriptions if possible (process multiple files)

## Audio Format

Supported:
- WAV, MP3, FLAC, OGG, M4A
- Auto-resampled to 16kHz
- Mono or stereo

## Deployment

See `DEPLOY.md` for VPS setup with Tailscale.
