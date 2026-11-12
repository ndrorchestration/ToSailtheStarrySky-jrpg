#!/usr/bin/env python3
"""Generate six ORIGINAL, deterministic 48kHz mono 16-bit QA ambience loops.

The sounds are deliberately low-fidelity synthetic test tones/noise, NOT
production Foley or recordings of real wildlife/crowds. They are authored
entirely by this script. Never synthesize into a game's Content/assets tree.
"""
from __future__ import annotations
import argparse
from array import array
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import wave

RATE = 48000
DURATION = 6.0
SAMPLES = int(RATE * DURATION)
LOOPS = (
    "harbor_surf_loop.wav",
    "harbor_gulls_loop.wav",
    "harbor_market_loop.wav",
    "weather_wind_loop.wav",
    "weather_rain_loop.wav",
    "weather_storm_loop.wav",
)
RECEIPT_STATUS = "ORIGINAL_HARBOR_LOOP_QA_ONLY_NOT_NATIVE_AUDITIONED"
MAX_PEAK = 0.56


def _smooth_periodic(noise: list[float], alpha: float) -> list[float]:
    state = 0.0
    # Iterate over identical ring to avoid a one-pole start-up transient.
    for _ in range(3):
        for value in noise:
            state = alpha * state + (1.0 - alpha) * value
    result = []
    for value in noise:
        state = alpha * state + (1.0 - alpha) * value
        result.append(state)
    return result


def pcm_for(name: str) -> bytes:
    if name not in LOOPS:
        raise ValueError("Unregistered synthetic QA loop: " + name)
    seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    white = [rng.uniform(-1.0, 1.0) for _ in range(SAMPLES)]
    middle = _smooth_periodic(white, 0.965)
    low = _smooth_periodic(white, 0.997)
    sound = []
    for idx in range(SAMPLES):
        t = idx / RATE
        turn = (2.0 * math.pi * idx) / SAMPLES
        medium = middle[idx]
        rumble = low[idx]
        if name == "harbor_surf_loop.wav":
            wavebed = 0.45 + 0.37 * math.cos(5 * turn - 0.6)
            sample = wavebed * (2.7 * medium + 2.8 * rumble)
        elif name == "harbor_gulls_loop.wav":
            sample = 0.12 * medium
            # Mock bird-like whistles: not field recordings.
            for center, hz, width in ((1.0, 940, .17), (2.9, 1320, .14), (4.75, 1050, .18)):
                distance = min(abs(t - center), DURATION - abs(t - center))
                chirp = math.exp(-0.5 * (distance / width) ** 2)
                sample += 0.38 * chirp * math.sin(2 * math.pi * hz * t
                                                  + 0.65 * math.sin(2 * math.pi * 9 * t))
        elif name == "harbor_market_loop.wav":
            # Diffuse synthetic murmurs, no spoken words or voice likeness.
            sample = (0.25 * math.sin(2 * math.pi * 126 * t + 11 * rumble)
                      + 0.18 * math.sin(2 * math.pi * 173 * t + 13 * medium)
                      + 1.6 * rumble) * (0.65 + 0.23 * math.cos(3 * turn))
        elif name == "weather_wind_loop.wav":
            sample = (3.2 * rumble + 1.2 * medium) * (0.50 + 0.40 * math.cos(2 * turn))
        elif name == "weather_rain_loop.wav":
            # High-frequency texture plus medium filtered patter.
            sample = (0.15 * white[idx] + 1.3 * medium + 0.25 * rumble) * (
                0.8 + 0.12 * math.cos(4 * turn))
        else:
            sample = (5.3 * rumble + 1.4 * medium
                      + 0.14 * math.sin(2 * math.pi * 42 * t)) * (
                          0.55 + 0.30 * math.cos(2 * turn))
        sound.append(sample)
    peak = max(abs(n) for n in sound)
    scale = MAX_PEAK / max(peak, 1.0e-9)
    sound = [max(-0.95, min(0.95, n * scale)) for n in sound]
    # Join exactly at the same PCM value. A 30-ms smooth correction prevents
    # the boundary from clicking without globally fading the ambience to zero.
    count = int(RATE * 0.03)
    join_correction = sound[0] - sound[-1]
    for k in range(count):
        t = (k + 1) / count
        s = t * t * (3.0 - 2.0 * t)
        sound[SAMPLES - count + k] += s * join_correction
    q = array("h", (int(round(max(-1.0, min(1.0, s)) * 32767)) for s in sound))
    if q.itemsize != 2:
        raise RuntimeError("Expected 16-bit PCM array")
    if q[0] != q[-1]:
        q[-1] = q[0]
    return q.tobytes()


def generate(output: Path) -> dict:
    output = Path(output).resolve()
    if {"content", "assets"} & {p.lower() for p in output.parts}:
        raise ValueError("Refusing QA synthesis inside Content or assets")
    if output.exists() and any(output.iterdir()):
        raise ValueError("Refusing to overwrite populated QA loop folder")
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in LOOPS:
        raw = pcm_for(name)
        p = output / name
        with wave.open(str(p), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(raw)
        rows.append({
            "filename": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            "duration_seconds": DURATION, "channels": 1,
            "sample_rate_hz": RATE, "rights": "ORIGINAL_SYNTHETIC_QA_ONLY",
            "production_approved": False, "looping_intent": True,
            "native_editor_verified": False,
        })
    receipt = {"version": "0.1", "status": RECEIPT_STATUS, "files": rows}
    (output / "harbor_loop_receipt.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def verify(folder: Path) -> list[Path]:
    folder = Path(folder).resolve(strict=True)
    if "content" in {p.lower() for p in folder.parts}:
        raise ValueError("QA loop source may not be inside Content")
    receipt = json.loads((folder / "harbor_loop_receipt.json").read_text(encoding="utf-8"))
    if receipt.get("status") != RECEIPT_STATUS:
        raise ValueError("Unapproved loop manifest")
    records = receipt.get("files", [])
    if (len(records) != len(LOOPS) or
            {r.get("filename") for r in records} != set(LOOPS)):
        raise ValueError("Loop source list mismatch")
    paths = []
    for entry in records:
        path = folder / entry["filename"]
        if not path.is_file() or path.is_symlink() or path.stat().st_size > 2_000_000:
            raise ValueError("Invalid QA loop path or file size")
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != entry.get("sha256"):
            raise ValueError("Loop checksum mismatch: " + path.name)
        with wave.open(str(path), "rb") as f:
            if (f.getnchannels(), f.getsampwidth(), f.getframerate(),
                f.getnframes()) != (1, 2, RATE, SAMPLES):
                raise ValueError("Loop PCM format mismatch")
            raw = f.readframes(f.getnframes())
        first = struct.unpack_from("<h", raw, 0)[0]
        last = struct.unpack_from("<h", raw, len(raw) - 2)[0]
        if abs(first - last) > 1:
            raise ValueError("QA sample loop discontinuity")
        if entry.get("production_approved") is not False or \
                entry.get("native_editor_verified") is not False or \
                entry.get("looping_intent") is not True:
            raise ValueError("QA release or loop status mismatch")
        paths.append(path)
    return paths


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    result = generate(parser.parse_args().output)
    print(json.dumps(result, indent=2))
