#!/usr/bin/env python3
"""
Test the improved audio chunking for >30s audio support.
"""

import wave
import sys
from pathlib import Path
import librosa
import soundfile as sf

# Force UTF-8 for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def get_audio_duration(wav_path: str) -> float:
    """Get audio duration in seconds."""
    try:
        with wave.open(wav_path, 'rb') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            return frames / rate
    except:
        return 0


def split_audio_chunks(wav_path: str, chunk_duration: int = 20) -> list:
    """Split WAV file into chunks before passing to Whisper (which has 30s limit)."""
    duration = get_audio_duration(wav_path)
    print(f"[OK] Audio duration: {duration:.1f}s")

    if duration <= chunk_duration:
        print(f"[OK] Audio is {duration:.1f}s (≤{chunk_duration}s), no split needed")
        return [wav_path]

    chunks = []
    try:
        # Load audio with librosa (this is safe, doesn't trigger model validation)
        print(f"[OK] Loading audio for splitting into {chunk_duration}s chunks...")
        y, sr = librosa.load(wav_path, sr=None)
        chunk_samples = int(chunk_duration * sr)

        for i, start in enumerate(range(0, len(y), chunk_samples)):
            chunk_audio = y[start:start + chunk_samples]
            chunk_path = wav_path.replace('.wav', f'_chunk_{i}.wav')

            # Write chunk WAV file
            sf.write(chunk_path, chunk_audio, sr)

            # Verify chunk duration
            chunk_dur = len(chunk_audio) / sr
            print(f"     Chunk {i}: {chunk_dur:.2f}s -> {chunk_path}")

            if chunk_dur > chunk_duration + 0.5:  # allow small tolerance
                print(f"[!!] Chunk {i} duration {chunk_dur}s exceeds limit, may fail")
            elif chunk_dur > 30:
                print(f"[ER] ERROR: Chunk {i} is {chunk_dur}s > 30s!")
                return None

            chunks.append(chunk_path)

    except Exception as e:
        print(f"[ER] Failed to split audio: {e}")
        return None

    print(f"[OK] Split into {len(chunks)} chunks")
    return chunks


def test_chunking():
    """Test chunking with 60-second audio."""
    test_file = "test_60.wav"

    print(f"\n{'='*60}")
    print(f"Testing audio chunking with {test_file}")
    print(f"{'='*60}\n")

    if not Path(test_file).exists():
        print(f"[ER] Test file not found: {test_file}")
        return False

    try:
        chunks = split_audio_chunks(test_file, chunk_duration=20)

        if chunks is None:
            print("\n[ER] Chunking failed!")
            return False

        # Verify chunks
        print(f"\n[OK] Verification:")
        for chunk in chunks:
            dur = get_audio_duration(chunk)
            if dur > 30:
                print(f"[ER] Chunk {chunk} is {dur:.2f}s > 30s (WILL FAIL)")
                return False
            else:
                print(f"     {chunk}: {dur:.2f}s [OK]")

        # Cleanup
        print(f"\n[OK] Cleaning up test chunks...")
        for chunk in chunks:
            if chunk != test_file:
                Path(chunk).unlink(missing_ok=True)

        print(f"\n{'='*60}")
        print(f"[OK] TEST PASSED: All chunks are <30s")
        print(f"{'='*60}\n")
        return True

    except Exception as e:
        print(f"\n[ER] Test error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_chunking()
    exit(0 if success else 1)
