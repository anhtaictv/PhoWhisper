# PhoWhisper Server Deployment Guide

## Architecture

```
QuanLyTinBai Application
         ↓
   PhoWhisper Client (client.py)
         ↓
   Tailscale VPN Network
         ↓
   VPS (phowhisper-server)
         ↓
   PhoWhisper API Server (FastAPI)
         ↓
   Whisper Model (HuggingFace)
```

## Prerequisites

- VPS with Docker & Docker Compose installed
- Tailscale account
- QuanLyTinBai application

## Quick Start (Docker)

### 1. On VPS: Setup & Deploy

```bash
# Clone repository
git clone https://github.com/VinAIResearch/PhoWhisper.git
cd PhoWhisper

# Create .env with Tailscale auth key
echo "TS_AUTHKEY=tskey-xxxxxxxxxxxx" > .env

# Start server
docker-compose up -d
```

### 2. Verify Server is Running

```bash
# Check health
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# List models
curl http://localhost:8000/models
```

### 3. Connect via Tailscale

```bash
# Get Tailscale IP
docker exec phowhisper-tailscale tailscale ip

# Or via hostname
ping phowhisper-server.tailxxxx.ts.net
```

## Using PhoWhisper from QuanLyTinBai

### Python Integration

```python
from client import PhoWhisperClient

# Connect to server via Tailscale
client = PhoWhisperClient(
    server_url="http://phowhisper-server.tailxxxx.ts.net:8000"
)

# Transcribe
text = client.transcribe("audio.wav", model="vinai/PhoWhisper-small")
print(text)
```

### cURL Example

```bash
# Upload audio file
curl -X POST http://phowhisper-server.tailxxxx.ts.net:8000/transcribe \
  -F "file=@audio.wav" \
  -F "model=vinai/PhoWhisper-small"
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | 0.0.0.0 | Server bind address |
| `SERVER_PORT` | 8000 | Server port |
| `USE_GPU` | 0 | Enable GPU (1=yes, 0=no) |
| `TS_AUTHKEY` | - | Tailscale auth key (required for Tailscale) |

## Performance Tuning

### GPU Support (NVIDIA)

```bash
# In docker-compose.yml, modify phowhisper service:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]

# Set env var
USE_GPU=1
```

### Model Selection

- **tiny**: 39M params, 500-1000ms per minute of audio
- **base**: 74M params, 1-2s per minute
- **small**: 244M params, 2-5s per minute (recommended)
- **medium**: 769M params, 5-10s per minute
- **large**: 1.55B params, 10-20s per minute

Smaller models are faster but less accurate.

### Memory Requirements

- **tiny**: 2GB RAM
- **base**: 3GB RAM
- **small**: 4GB RAM
- **medium**: 6GB RAM
- **large**: 8GB RAM

## Monitoring

### View Logs

```bash
# Server logs
docker logs phowhisper-server

# Follow logs
docker logs -f phowhisper-server

# Tailscale logs
docker logs phowhisper-tailscale
```

### Health Check

```bash
# Server status
docker ps

# Model cache size
docker exec phowhisper-server du -sh /root/.cache/huggingface
```

## Troubleshooting

### Server not responding

```bash
# Check if containers running
docker ps | grep phowhisper

# Restart
docker-compose restart phowhisper

# Full restart
docker-compose down && docker-compose up -d
```

### Out of Memory

```bash
# Use smaller model
docker-compose down
# Edit docker-compose.yml, change model in env
docker-compose up -d
```

### Tailscale connection issues

```bash
# Check Tailscale status
docker exec phowhisper-tailscale tailscale status

# Recreate auth key if expired
docker-compose down
echo "TS_AUTHKEY=tskey-xxxxxxxxxxxx" > .env
docker-compose up -d
```

### Slow transcription

```bash
# Enable GPU if available
echo "USE_GPU=1" >> .env
docker-compose restart phowhisper

# Or use smaller model (tiny, base)
```

## Production Setup

### 1. System Configuration

```bash
# Increase file descriptors
ulimit -n 65536

# Enable persistence
echo "vm.overcommit_memory=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. Secure with Reverse Proxy

```nginx
# nginx config
upstream phowhisper {
    server localhost:8000;
}

server {
    listen 80;
    server_name phowhisper.example.com;

    location / {
        proxy_pass http://phowhisper;
        proxy_request_buffering off;
        proxy_http_version 1.1;
        client_max_body_size 100M;  # Max audio file size
    }
}
```

### 3. Rate Limiting

Add to docker-compose.yml environment:
```yaml
environment:
  - RATELIMIT_ENABLED=1
  - RATELIMIT_REQUESTS=10
  - RATELIMIT_WINDOW=60
```

### 4. Model Caching

Models are cached in Docker volume `model-cache`. To pre-download:

```bash
docker exec phowhisper-server python -c "
from transformers import pipeline
pipeline('automatic-speech-recognition', model='vinai/PhoWhisper-small')
"
```

## Backup & Updates

### Backup Model Cache

```bash
docker exec phowhisper-server tar -czf - /root/.cache/huggingface > models.tar.gz
```

### Update Models

```bash
# Pull latest code
git pull

# Rebuild
docker-compose build --no-cache

# Restart
docker-compose down && docker-compose up -d
```

## Support

- Model info: https://huggingface.co/vinai/PhoWhisper-small
- FastAPI docs: `http://server:8000/docs` (Swagger UI)
- RedDoc: `http://server:8000/redoc`
