#!/usr/bin/env python3
"""Generate TWO original deterministic review-only Resonator spell sound effects.

No commercial game sound samples, network calls, or pre-existing music.
Only ever creates WAVs under review/ResonatorFocus/AudioSource; no overwrite.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import struct
import wave

RATE=24000
DURATIONS={"SFX_Centering":1.42,"SFX_ResonantPulse":.94}

def samples(name):
    if name not in DURATIONS: raise ValueError("unknown name")
    rnd=random.Random(619219+list(DURATIONS).index(name))
    duration=DURATIONS[name]
    out=bytearray()
    for i in range(round(RATE*duration)):
        t=i/RATE
        fade=min(1.,t/.025)*min(1.,(duration-t)/.16)
        if name=="SFX_Centering":
            base=(math.sin(2*math.pi*196*t)+.48*math.sin(2*math.pi*293.66*t)
                  +.36*math.sin(2*math.pi*391.99*t))
            ripple=.16*math.sin(2*math.pi*(392*t+45*t*t))
            val=fade*(.22*base+.16*ripple+
                .04*rnd.uniform(-1.,1.)*math.sin(math.pi*t/duration))
        else:
            rising=math.sin(2*math.pi*(185*t+650*t*t/(2*duration)))
            glass=math.sin(2*math.pi*880*t)*math.exp(-4.1*t/duration)
            noise=rnd.uniform(-1.,1.)*math.exp(-6*t/duration)
            val=fade*(.40*rising+.24*glass+.10*noise)
        out.extend(struct.pack("<h",round(max(-.88,min(.88,val))*32767)))
    return bytes(out)

def generate(path):
    path=path.resolve()
    if path.name!="AudioSource" or path.parent.name!="ResonatorFocus" or path.parent.parent.name!="Review":
        raise RuntimeError("refuse out-of-scope audio write")
    path.mkdir(parents=True,exist_ok=True)
    for name in DURATIONS:
        if (path/(name+".wav")).exists():
            raise RuntimeError("refuse overwrite "+name)
    manifest={"version":"TSTSS_EnderResonatorReview_SFX1",
              "sample_rate":RATE,"original_synthetic_audio":True,"files":{}}
    for name in DURATIONS:
        f=path/(name+".wav")
        with f.open("xb") as stream:
            with wave.open(stream,"wb") as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(RATE)
                wav.writeframes(samples(name))
        manifest["files"][name]={"bytes":f.stat().st_size,
                "duration":DURATIONS[name],
                "sha256":hashlib.sha256(f.read_bytes()).hexdigest()}
    return manifest

def main():
    p=argparse.ArgumentParser(description=__doc__)
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--validate",action="store_true")
    g.add_argument("--generate",type=Path)
    a=p.parse_args()
    print(json.dumps({"status":"SOURCE_ONLY","names":list(DURATIONS)}
        if a.validate else generate(a.generate),indent=2))
if __name__=="__main__":main()
