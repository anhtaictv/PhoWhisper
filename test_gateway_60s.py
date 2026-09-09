#!/usr/bin/env python3
"""
Test gateway /transcribe endpoint with 60-second audio.
"""

import sys
import io
import requests
import time
from pathlib import Path

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GATEWAY_URL = "http://localhost:3000"
TEST_FILE = "test_60.wav"


def test_gateway_transcribe():
    """Test gateway transcribe endpoint."""

    if not Path(TEST_FILE).exists():
        print(f"[ER] Test file not found: {TEST_FILE}")
        return False

    print(f"\n{'='*70}")
    print(f"Testing Gateway Transcribe Endpoint with 60-second Audio")
    print(f"{'='*70}\n")

    # Read audio file
    with open(TEST_FILE, 'rb') as f:
        audio_data = f.read()

    print(f"[OK] Loaded audio file: {TEST_FILE} ({len(audio_data)} bytes)")

    # Test endpoint
    endpoint = f"{GATEWAY_URL}/transcribe"
    print(f"[OK] Endpoint: {endpoint}")
    print(f"[..] Sending request to gateway...\n")

    start_time = time.time()

    try:
        response = requests.post(
            endpoint,
            files={"audio": ("test_60.wav", audio_data, "audio/wav")},
            timeout=300  # 5 minute timeout
        )

        elapsed = time.time() - start_time

        print(f"\n[OK] Response received in {elapsed:.1f}s")
        print(f"[OK] Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] SUCCESS!")
            print(f"     Model: {data.get('model')}")
            print(f"     Text length: {len(data.get('text', ''))} chars")

            text = data.get('text', '')
            if text:
                preview = text[:200] + ("..." if len(text) > 200 else "")
                print(f"     Preview: {preview}")
                print(f"\n[OK] Full transcription:")
                print(f"     {text}")
            else:
                print(f"[!!] Empty transcription result")

            print(f"\n{'='*70}")
            print(f"[OK] TEST PASSED: 60-second audio transcribed successfully!")
            print(f"{'='*70}\n")
            return True

        else:
            print(f"[ER] Error response:")
            print(f"     {response.text}")
            return False

    except requests.exceptions.Timeout:
        print(f"[ER] Request timeout after 300s")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"[ER] Connection error: {e}")
        print(f"[..] Make sure gateway is running on port 3000")
        return False
    except Exception as e:
        print(f"[ER] Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_gateway_transcribe()
    exit(0 if success else 1)
