#!/usr/bin/env python3
"""
Test 3-minute (180-second) audio support via server and gateway endpoints.
"""

import sys
import io
import requests
import base64
import time
from pathlib import Path

# Force UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SERVER_URL = "http://localhost:8000"
GATEWAY_URL = "http://localhost:3000"
TEST_FILE = "test_180s.wav"


def test_server_180s():
    """Test server with 3-minute audio."""

    if not Path(TEST_FILE).exists():
        print(f"[ER] Test file not found: {TEST_FILE}")
        return False

    print(f"\n{'='*70}")
    print(f"Testing Server /api/transcribe with 3-Minute Audio (180s)")
    print(f"{'='*70}\n")

    # Read and encode audio
    with open(TEST_FILE, 'rb') as f:
        audio_data = f.read()

    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    print(f"[OK] Loaded audio file: {TEST_FILE} ({len(audio_data)} bytes)")

    endpoint = f"{SERVER_URL}/api/transcribe"
    print(f"[OK] Endpoint: {endpoint}")
    print(f"[..] Sending request to server...\n")

    start_time = time.time()

    try:
        response = requests.post(
            endpoint,
            json={"audio": audio_b64, "model": "vinai/PhoWhisper-small"},
            timeout=300
        )

        elapsed = time.time() - start_time

        print(f"\n[OK] Response received in {elapsed:.1f}s")
        print(f"[OK] Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] SUCCESS!")
            print(f"     Model: {data.get('model')}")
            text = data.get('text', '')
            print(f"     Text length: {len(text)} chars")

            if text:
                preview = text[:300] + ("..." if len(text) > 300 else "")
                print(f"     Preview: {preview}")
            else:
                print(f"[!!] Empty transcription result")

            return True
        else:
            print(f"[ER] Error response: {response.text}")
            return False

    except Exception as e:
        print(f"[ER] Error: {e}")
        return False


def test_gateway_180s():
    """Test gateway with 3-minute audio."""

    if not Path(TEST_FILE).exists():
        print(f"[ER] Test file not found: {TEST_FILE}")
        return False

    print(f"\n{'='*70}")
    print(f"Testing Gateway /transcribe with 3-Minute Audio (180s)")
    print(f"{'='*70}\n")

    # Read audio
    with open(TEST_FILE, 'rb') as f:
        audio_data = f.read()

    print(f"[OK] Loaded audio file: {TEST_FILE} ({len(audio_data)} bytes)")

    endpoint = f"{GATEWAY_URL}/transcribe"
    print(f"[OK] Endpoint: {endpoint}")
    print(f"[..] Sending request to gateway...\n")

    start_time = time.time()

    try:
        response = requests.post(
            endpoint,
            files={"audio": ("test_180s.wav", audio_data, "audio/wav")},
            timeout=300
        )

        elapsed = time.time() - start_time

        print(f"\n[OK] Response received in {elapsed:.1f}s")
        print(f"[OK] Status code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n[OK] SUCCESS!")
            print(f"     Model: {data.get('model')}")
            text = data.get('text', '')
            print(f"     Text length: {len(text)} chars")

            if text:
                preview = text[:300] + ("..." if len(text) > 300 else "")
                print(f"     Preview: {preview}")
            else:
                print(f"[!!] Empty transcription result")

            return True
        else:
            print(f"[ER] Error response: {response.text}")
            return False

    except Exception as e:
        print(f"[ER] Error: {e}")
        return False


if __name__ == "__main__":
    print("\n[**] Testing 3-Minute (180-second) Audio Support\n")

    server_ok = test_server_180s()
    gateway_ok = test_gateway_180s()

    print(f"\n{'='*70}")
    print(f"Test Results:")
    print(f"  Server:  {'PASS' if server_ok else 'FAIL'}")
    print(f"  Gateway: {'PASS' if gateway_ok else 'FAIL'}")
    print(f"{'='*70}\n")

    exit(0 if (server_ok and gateway_ok) else 1)
