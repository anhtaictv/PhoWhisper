#!/usr/bin/env python3
"""
PhoWhisper API Server - Ollama-style
Simple Vietnamese ASR API with long-form audio support
"""

from fastapi import FastAPI, HTTPException
import uvicorn
import tempfile
import base64
from pathlib import Path
from transformers import pipeline
import logging
import os
import wave
import librosa
import soundfile as sf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PhoWhisper", version="1.0.0")

_transcriber = None
_current_model = "vinai/PhoWhisper-small"

def get_transcriber(model: str = "vinai/PhoWhisper-small"):
    """Load and cache transcriber model."""
    global _transcriber, _current_model
    if _transcriber is None or _current_model != model:
        logger.info(f"Loading model: {model}")
        device = 0 if os.environ.get("USE_GPU") else -1
        _transcriber = pipeline(
            "automatic-speech-recognition",
            model=model,
            device=device,
            trust_remote_code=True,
            model_kwargs={"num_beams": 1}
        )
        _current_model = model
    return _transcriber

def get_audio_duration(wav_path: str) -> float:
    """Get audio duration in seconds."""
    try:
        with wave.open(wav_path, 'rb') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / rate
    except:
        return 0

def split_audio_chunks(wav_path: str, chunk_duration: int = 25) -> list:
    """Split WAV file into chunks to avoid >30s limit."""
    duration = get_audio_duration(wav_path)
    if duration <= chunk_duration:
        return [wav_path]

    chunks = []
    try:
        # Load audio with librosa
        y, sr = librosa.load(wav_path, sr=None)
        chunk_samples = chunk_duration * sr

        for i, start in enumerate(range(0, len(y), chunk_samples)):
            chunk_audio = y[start:start + chunk_samples]
            chunk_path = wav_path.replace('.wav', f'_chunk_{i}.wav')
            sf.write(chunk_path, chunk_audio, sr)
            chunks.append(chunk_path)
            logger.info(f"Created chunk {i}: {len(chunk_audio)/sr:.1f}s")
    except Exception as e:
        logger.warning(f"Failed to split audio: {e}, using whole file")
        return [wav_path]

    return chunks

@app.get("/")
async def root():
    """API info."""
    return {"name": "PhoWhisper", "version": "1.0.0"}

@app.post("/api/transcribe")
async def transcribe(request: dict):
    """
    Transcribe audio (Ollama-style API).
    Supports unlimited audio length with automatic chunking.

    Request JSON:
    {
        "audio": "base64_encoded_audio_data",
        "model": "vinai/PhoWhisper-small"  # optional
    }

    Response:
    {
        "text": "transcribed text",
        "model": "vinai/PhoWhisper-small"
    }
    """
    if "audio" not in request:
        raise HTTPException(status_code=400, detail="Missing 'audio' field")

    phowhisper_model = request.get("model", "vinai/PhoWhisper-small")
    whisper_model_name = map_model_name(phowhisper_model)

    try:
        # Decode base64 audio
        audio_data = base64.b64decode(request["audio"])

        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        # Transcribe with pipeline
        transcriber = get_transcriber(phowhisper_model)
        logger.info(f"Transcribing with {phowhisper_model}")

        # Split long audio into 25-second chunks to avoid model limit
        chunks = split_audio_chunks(tmp_path, chunk_duration=25)
        texts = []

        for chunk_path in chunks:
            try:
                result = transcriber(chunk_path)
                texts.append(result.get("text", ""))
            finally:
                if chunk_path != tmp_path:
                    Path(chunk_path).unlink(missing_ok=True)

        # Cleanup
        Path(tmp_path).unlink(missing_ok=True)

        return {
            "text": " ".join(texts).strip(),
            "model": phowhisper_model
        }

    except Exception as e:
        logger.error(f"Transcription error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tags")
async def list_models():
    """List available models (Ollama-style)."""
    return {
        "models": [
            {"name": "vinai/PhoWhisper-tiny", "size": "39M"},
            {"name": "vinai/PhoWhisper-base", "size": "74M"},
            {"name": "vinai/PhoWhisper-small", "size": "244M"},
            {"name": "vinai/PhoWhisper-medium", "size": "769M"},
            {"name": "vinai/PhoWhisper-large", "size": "1.55B"},
        ]
    }

if __name__ == "__main__":
    host = os.environ.get("SERVER_HOST", "0.0.0.0")
    port = int(os.environ.get("SERVER_PORT", 8000))

    logger.info(f"Starting PhoWhisper server on {host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")
