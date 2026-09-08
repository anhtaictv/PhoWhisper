# PhoWhisper Setup Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify installation:**
   ```bash
   python -c "from transformers import pipeline; print('OK')"
   ```

## Quick Start

### Basic usage:
```bash
python example.py path/to/audio.wav
```

### In Python:
```python
from transformers import pipeline

transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small")
text = transcriber("audio.wav")['text']
print(text)
```

## Model Selection

| Model | Size | Speed | Accuracy | Params |
|-------|------|-------|----------|--------|
| tiny | ⚡⚡⚡ | Fastest | 19.05 WER | 39M |
| base | ⚡⚡ | Fast | 16.19 WER | 74M |
| small | ⚡ | Balanced | **11.08 WER** | 244M |
| medium | - | Slow | 8.27 WER | 769M |
| large | - | Slowest | **8.14 WER** | 1.55B |

**Recommended:** `vinai/PhoWhisper-small` for most use cases.

## Audio Format

Input audio should be:
- Format: WAV, MP3, FLAC, OGG
- Sample rate: 16 kHz (automatically resampled if needed)
- Mono or stereo (both supported)

## System Requirements

- **RAM:** 8GB+ (4GB minimum with small model)
- **GPU:** Optional (CUDA 11.8+ recommended for speed)
- **Disk:** ~2GB for model cache

## Troubleshooting

**Out of memory?** Use smaller model:
```python
pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-tiny")
```

**Slow inference?** Enable GPU:
```python
pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-small", device=0)
```

**Can't find audio file?** Check path is absolute or relative to current directory.
