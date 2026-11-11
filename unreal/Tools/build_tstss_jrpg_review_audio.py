#!/usr/bin/env python3
"""Generate four ORIGINAL, deterministic review-only JRPG transition sound effects.

These sound effects are newly synthesized (not sampled, quoted or adapted from
a commercial game). They are provisional sound design, not a scored soundtrack.
No external dependencies or network calls. By default read-only --validate.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
import random
from pathlib import Path
import struct
import wave

RATE=24000
RECIPE_VERSION="TSTSS_JRPG_REVIEW_SFX_V1"
NAMES=("SFX_EncounterSting","SFX_VictoryFanfare",
       "SFX_RewardReveal","SFX_ReturnWhoosh")
SECONDS={"SFX_EncounterSting":.95,
         "SFX_VictoryFanfare":2.20,
         "SFX_RewardReveal":1.15,
         "SFX_ReturnWhoosh":.72}


def env(t,d):
    return min(1.0,t/.018)*min(1.0,(d-t)/.12) if 0<=t<d else 0.


def harmonic(f,t):
    return (math.sin(2*math.pi*f*t)
            +.25*math.sin(4*math.pi*f*t)
            +.10*math.sin(6*math.pi*f*t))/1.35


def sample(name,t,noise):
    duration=SECONDS[name]
    fade=env(t,duration)
    if name=="SFX_EncounterSting":
        # Rising airy shimmer ending in a short chord.
        pitch=310.0+930.0*(t/duration)**1.5
        tone=math.sin(2*math.pi*(310*t+930*t**2/(2*duration)))
        sparkle=math.sin(2*math.pi*pitch*t)*.26
        tail=harmonic(620,t)*max(0.,(t-.44)/duration)
        return fade*(.38*tone+.25*sparkle+.22*tail+.16*noise*math.sin(math.pi*t/duration))
    if name=="SFX_VictoryFanfare":
        # Original synthetic fanfare: four overlapping triad notes with
        # individualized envelope and bright non-brass harmonics.
        # The notes are tonal building blocks, not a transcription.
        phrase=((0.00,523.25,.38),(0.31,659.25,.43),
                (0.67,783.99,.48),(1.02,1046.5,1.03))
        value=0.
        for start,freq,length in phrase:
            rel=t-start
            if 0<=rel<length:
                a=min(1.,rel/.025)*min(1.,(length-rel)/.19)
                value+=a*harmonic(freq,rel)
        bass=math.sin(2*math.pi*261.63*t)*.10 if .95<t<2.08 else 0.
        return fade*(.36*value+bass+.018*noise)
    if name=="SFX_RewardReveal":
        # Quiet crystalline triad; a subtle reveal under an item panel.
        notes=((0.0,880.0,.48),(.19,1174.66,.52),(.40,1396.91,.70))
        v=0.
        for start,freq,length in notes:
            rel=t-start
            if 0<=rel<length:
                a=min(1.,rel/.008)*math.exp(-3.0*rel/length)
                v+=a*(math.sin(2*math.pi*freq*rel)+.4*math.sin(4*math.pi*freq*rel))
        return fade*.29*v
    if name=="SFX_ReturnWhoosh":
        sweep=620.0-430*(t/duration)
        tone=math.sin(2*math.pi*(620*t-430*t*t/(2*duration)))
        return fade*(.24*tone+.21*noise*(1-t/duration)+.07*math.sin(2*math.pi*sweep*t))
    raise ValueError(name)


def build_pcm(name):
    if name not in NAMES:
        raise ValueError("unknown sound recipe")
    rnd=random.Random(0x4A525047+NAMES.index(name))
    count=round(RATE*SECONDS[name])
    data=bytearray()
    for index in range(count):
        amp=sample(name,index/RATE,rnd.uniform(-1.,1.))
        amp=max(-.86,min(.86,amp))
        data+=struct.pack("<h",int(amp*32767))
    return bytes(data)


def generate(root:Path):
    root=root.resolve()
    if root.name != "AudioSource" or root.parent.name != "Review":
        raise RuntimeError("HOLD: audio sources must remain under review namespace")
    result={"recipe_version":RECIPE_VERSION,"sample_rate":RATE,
            "assets":{},"original_synthetic_audio":True}
    for name in NAMES:
        path=root/(name+".wav")
        if path.exists():
            raise RuntimeError("HOLD: refuse audio source overwrite "+str(path))
    root.mkdir(parents=True,exist_ok=True)
    for name in NAMES:
        path=root/(name+".wav")
        with path.open("xb") as raw:
            with wave.open(raw,"wb") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(RATE)
                f.writeframes(build_pcm(name))
        result["assets"][name]={
            "sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes":path.stat().st_size,
            "seconds":SECONDS[name]}
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate",action="store_true")
    group.add_argument("--generate",type=Path)
    args=parser.parse_args()
    if args.validate:
        out={"status":"SOURCE_RECIPE_ONLY","recipes":list(NAMES),
             "sample_rate":RATE,"version":RECIPE_VERSION,
             "no_music_or_commercial_samples":True}
    else:
        out=generate(args.generate)
    print(json.dumps(out,indent=2))

if __name__=="__main__":
    main()
