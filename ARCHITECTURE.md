# PhoWhisper Architecture

## System Overview

```
┌─────────────────────┐
│  QuanLyTinBai       │
│  (AI Application)   │
└──────────┬──────────┘
           │
           │ HTTP (JSON)
           │
┌──────────▼──────────┐
│  AI Gateway         │
│  (your server)      │
└──────────┬──────────┘
           │
           │ HTTP over Tailscale
           │
┌──────────▼──────────────────┐
│  Tailscale VPN Network      │
│  (secure tunnel)            │
└──────────┬──────────────────┘
           │
┌──────────▼──────────────────┐
│  VPS (phowhisper-server)    │
│  • PhoWhisper FastAPI       │
│  • Tailscale Client         │
│  • Docker Container         │
│  • Whisper Models Cache     │
└────────────────────────────┘
```

## API Flow

```
POST /api/transcribe
{
  "audio": "base64_audio_data",
  "model": "vinai/PhoWhisper-small"
}

        ↓ (1-20s depending on model)

{
  "text": "Xin chào",
  "model": "vinai/PhoWhisper-small"
}
```

## Files Structure

```
PhoWhisper/
├── server.py              # FastAPI server (Ollama-style)
├── client.py              # Python client library
├── Dockerfile             # Container image
├── docker-compose.yml     # Tailscale + PhoWhisper orchestration
├── requirements.txt       # Python dependencies
├── .env.example          # Configuration template
├── API.md                # API documentation
├── DEPLOY.md             # Deployment guide
├── ARCHITECTURE.md       # This file
├── SETUP.md              # Local development
├── example.py            # Standalone example
└── README.md             # Original PhoWhisper info
```

## Deployment Steps

### 1. On VPS

```bash
git clone https://github.com/VinAIResearch/PhoWhisper.git
cd PhoWhisper
cp .env.example .env
# Edit .env with Tailscale auth key
docker-compose up -d
```

### 2. In AI Gateway

```python
from client import PhoWhisperClient

client = PhoWhisperClient(
    server_url="http://phowhisper-server.tailxxxx.ts.net:8000"
)

# Use it
text = client.transcribe("audio.wav")
```

## Key Features

✅ **Ollama-style API** - Simple, familiar interface  
✅ **Tailscale VPN** - Secure encrypted connection  
✅ **Docker Ready** - One-command deployment  
✅ **Model Selection** - 5 sizes (39M - 1.55B)  
✅ **Async Support** - FastAPI async endpoints  
✅ **Health Checks** - Built-in monitoring  

## Configuration

Environment variables in `.env`:

```
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
USE_GPU=0              # Set 1 for NVIDIA GPU
TS_AUTHKEY=tskey-xxx   # Tailscale auth key
```

## Performance

Model inference times (per minute of audio):

| Model | CPU | GPU |
|-------|-----|-----|
| tiny | 1s | 0.5s |
| small | 5s | 2s |
| large | 20s | 8s |

## Security

- 🔒 Tailscale: End-to-end encrypted
- 🔒 Docker: Isolated container
- 🔒 API: JSON-based (no file uploads)
- 🔒 Models: From official HuggingFace

## Monitoring

```bash
# Check server status
docker ps | grep phowhisper

# View logs
docker logs -f phowhisper-server

# Check model cache
docker exec phowhisper-server du -sh /root/.cache/huggingface
```

## Troubleshooting

**Server not responding?**
```bash
docker-compose restart phowhisper
```

**Out of memory?**
```bash
# Use smaller model in docker-compose.yml
USE_SMALL_MODEL=1
```

**Slow transcription?**
```bash
# Enable GPU
USE_GPU=1 docker-compose up -d
```
