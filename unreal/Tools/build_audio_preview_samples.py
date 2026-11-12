#!/usr/bin/env python3
"""Make deterministic ORIGINAL QA-only WAV sound sketches, never licensed music.
Run: python unreal/Tools/build_audio_preview_samples.py --output <scratch-folder>
Do not confuse these primitive synthetic checks with production Foley or native audio QA.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import wave

RATE = 48000
DURATIONS = {
    "ui_confirm.wav": 0.44,
    "repair_attuned.wav": 1.50,
    "engine_warning.wav": 2.30,
    "mystery_echo.wav": 3.10,
    "weather_gust.wav": 2.20,
    "splashdown_review.wav": 1.80,
    "footstep_wood.wav": 0.35,
    "footstep_sand.wav": 0.38,
    "footstep_stone.wav": 0.32,
    "footstep_metal.wav": 0.44,
}

def envelope(t, duration, attack=0.025, release=0.14):
    return max(0.0, min(1.0, t / attack, (duration - t) / release))

def make_pcm(name, duration):
    if name not in DURATIONS or duration != DURATIONS[name]:
        raise ValueError("Unregistered review sound")
    seed = int.from_bytes(hashlib.sha256(name.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    samples = []
    lowpass = 0.0
    for n in range(round(duration * RATE)):
        t = n / RATE
        noise = rng.uniform(-1.0, 1.0)
        lowpass = 0.99 * lowpass + 0.01 * noise
        env = envelope(t, duration)
        if name == "ui_confirm.wav":
            first = math.sin(2*math.pi*659.25*t) * math.exp(-16*t)
            delta = max(t - 0.12, 0.0)
            second = 0.45*math.sin(2*math.pi*880*delta)*math.exp(-13*delta) if t >= 0.12 else 0.0
            x = (first + second)*env
        elif name == "repair_attuned.wav":
            mix = min(1.0, t / 0.7)
            x = (0.50*math.sin(2*math.pi*220*t)
                 +0.29*math.sin(2*math.pi*(277.18 + 6*mix)*t)
                 +0.22*math.sin(2*math.pi*329.63*t))*env
        elif name == "engine_warning.wav":
            wobble = 6.0*math.sin(2*math.pi*3.2*t)
            x = (0.50*math.sin(2*math.pi*(79 + wobble)*t)
                 +0.20*math.sin(2*math.pi*158*t)
                 +0.50*lowpass)*env
        elif name == "mystery_echo.wav":
            tremolo = 0.45 + 0.55*math.cos(2*math.pi*0.48*t)**2
            x = (0.44*math.sin(2*math.pi*110*t)
                 +0.21*math.sin(2*math.pi*138.59*t)
                 +0.12*math.sin(2*math.pi*164.81*t)
                 +0.18*lowpass)*env*tremolo
        elif name == "weather_gust.wav":
            modulation = 0.5 + 0.4*math.sin(2*math.pi*0.36*t)
            x = (3.0*lowpass + 0.10*noise)*env*modulation
        elif name == "footstep_wood.wav":
            x = (0.75*math.sin(2*math.pi*85*t)*math.exp(-24*t)
                 +0.23*noise*math.exp(-35*t))*env
        elif name == "footstep_sand.wav":
            x = (0.58*noise*math.exp(-16*t)
                 +2.0*lowpass*math.exp(-12*t))*env
        elif name == "footstep_stone.wav":
            x = (0.49*noise*math.exp(-41*t)
                 +0.76*math.sin(2*math.pi*180*t)*math.exp(-25*t))*env
        elif name == "footstep_metal.wav":
            x = (0.64*math.sin(2*math.pi*412*t)*math.exp(-17*t)
                 +0.34*math.sin(2*math.pi*679*t)*math.exp(-23*t)
                 +0.14*noise*math.exp(-38*t))*env
        else:
            x = (0.7*noise*math.exp(-9*t) + 2.3*lowpass*math.exp(-1.5*t))*env
        samples.append(x)
    peak = max(abs(x) for x in samples)
    scale = 0.66 / max(peak, 1e-9)
    return b"".join(struct.pack("<h", int(max(-32767, min(32767, round(x*scale*32767))))) for x in samples)

def generate(output):
    output = Path(output).resolve()
    if {"content", "assets"} & {part.lower() for part in output.parts}:
        raise ValueError("Refusing review synthesis inside packaged Content or assets")
    output.mkdir(parents=True, exist_ok=True)
    files = []
    for name, duration in sorted(DURATIONS.items()):
        dest = output / name
        pcm = make_pcm(name, duration)
        with wave.open(str(dest), "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(RATE)
            f.writeframes(pcm)
        files.append({"filename":name, "sha256":hashlib.sha256(dest.read_bytes()).hexdigest(),
                      "duration_seconds":round(len(pcm)/(2*RATE), 6),
                      "channels":1, "sample_rate_hz":RATE, "rights":"ORIGINAL_QA_ONLY",
                      "production_approved":False})
    receipt={"version":"0.1","status":"ORIGINAL_REVIEW_SYNTHETIC_NOT_NATIVE_VERIFIED","files":files}
    (output / "audio_preview_receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    print(json.dumps(generate(parser.parse_args().output),indent=2))
