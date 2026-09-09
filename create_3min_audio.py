#!/usr/bin/env python3
"""
Create a 3-minute (180 second) test audio file by repeating 60-second audio.
"""

import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

def create_3min_audio():
    """Create 3-minute audio by repeating 60-second audio 3 times."""

    source_file = "test_60.wav"
    output_file = "test_180s.wav"

    print(f"Creating {output_file} from {source_file}...")

    if not Path(source_file).exists():
        print(f"Error: {source_file} not found")
        return False

    # Load 60-second audio
    y, sr = librosa.load(source_file, sr=None)
    print(f"[OK] Loaded {source_file}: {len(y)/sr:.1f}s")

    # Repeat 3 times to get 180 seconds
    y_3min = np.concatenate([y, y, y])

    # Save
    sf.write(output_file, y_3min, sr)

    # Verify
    duration = len(y_3min) / sr
    print(f"[OK] Created {output_file}: {duration:.1f}s")

    return True

if __name__ == "__main__":
    success = create_3min_audio()
    exit(0 if success else 1)
