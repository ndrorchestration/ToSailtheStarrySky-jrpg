#!/usr/bin/env python3
"""Build two deterministic, NONCANONICAL sky/ocean review textures.

Pure stdlib. These are inexpensive lighting/composition studies, not physically
simulated seawater, a finalized biome, or canon auroral-lane art.
"""
from __future__ import annotations
import argparse,hashlib,json,math,struct,zlib
from pathlib import Path

STATUS="NONCANONICAL_ENVIRONMENT_LOOKDEV_NOT_GAMEPLAY"
SKY="AureateWake_SkyReviewV1.png"
SEA="AureateWake_OceanReviewV1.png"
MANIFEST="AureateWake_SkySeaReviewV1_Manifest.json"
SIZE=(512,256)
SEA_SIZE=(512,512)

def clamp(x):return max(0,min(1,x))
def mix(a,b,t):return a*(1-t)+b*t

def png(width,height,pixels):
    if len(pixels)!=width*height*4:raise ValueError("incorrect pixel count")
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data)&0xffffffff)
    rows=b"".join(b"\0"+pixels[y*width*4:(y+1)*width*4] for y in range(height))
    return (b"\x89PNG\r\n\x1a\n"+
      chunk(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0))+
      chunk(b"IDAT",zlib.compress(rows,9))+chunk(b"IEND",b""))

def sky_pixel(x,y):
    w,h=SIZE
    u=x/(w-1);v=y/(h-1)
    # Top-down panoramic sky mapping (north/zenith blue, warm horizon at v~0.5)
    hdist=abs(v-.5)*2
    upper=(.016,.078,.18)
    horizon=(.39,.60,.68)
    t=clamp(hdist**.80)
    col=[mix(horizon[i],upper[i],t) for i in range(3)]
    # Warm sunset band concentrated at a single azimuth, restrained so
    # four-wing materials remain legible rather than drowned in bloom.
    dist=min(abs(u-.69),1-abs(u-.69))
    warmth=math.exp(-((dist/.135)**2)-(((v-.48)/.13)**2))
    for i,warm in enumerate((.54,.19,.075)):
        col[i]+=warm*warmth
    # Procedural high-altitude cloud wisps, no external image/asset licensing.
    cloud=math.sin(23*u+11*v)*math.sin(41*u-19*v)+.5*math.sin(83*u+5*v)
    cloud=clamp((cloud-.58)/1.0)*.16*(1-hdist)
    return tuple(round(255*clamp(c+cloud)) for c in col)+(255,)

def ocean_pixel(x,y):
    w,h=SEA_SIZE;u=x/w;v=y/h
    long=math.sin(math.tau*(14*u+1.6*math.sin(math.tau*3*v)))
    chop=math.sin(math.tau*(39*v+3*u))*.28
    weave=math.sin(math.tau*(37*u+24*v))*.12
    val=long*.50+chop+weave
    foam=clamp((val-.40)*.42)
    base=(.021,.18,.235)
    return tuple(round(255*clamp(c+val*d+foam*.12)) for c,d in zip(base,(.012,.035,.048)))+(255,)

def raster(size,fn):
    w,h=size;data=bytearray()
    for y in range(h):
        for x in range(w):data.extend(fn(x,y))
    return png(w,h,bytes(data))

def build():
    assets={SKY:raster(SIZE,sky_pixel),SEA:raster(SEA_SIZE,ocean_pixel)}
    manifest={
        "status":STATUS,
        "scene":"noncanonical Aureate Wake atmosphere and ocean visual-review only",
        "source_units":"centimeters",
        "sky_dimensions":list(SIZE),"ocean_dimensions":list(SEA_SIZE),
        "sha256":{k:hashlib.sha256(v).hexdigest() for k,v in assets.items()},
        "target_assets":"/Game/TSTSS/Review/Environment/SkySeaV1",
        "target_scene":"/Game/TSTSS/Review/Scenes/AureateWakeSkyborne_SkySeaReviewV1",
        "source_scene":"/Game/TSTSS/Review/Scenes/AureateWakeSkyborne_WingUVRepairV3",
        "no_existing_map_or_asset_overwrite":True,
        "art_authority":"NONCANONICAL",
        "orbiter":"LOCKED",
        "limitations":["Not an ocean simulation","No water buoyancy or underwater physics",
          "Not final atmospheric color grading","No cinematic-material approval",
          "No new gameplay, First Wake scene, canon, form unlock or deployment"]
    }
    return assets,manifest

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True,type=Path)
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args(argv)
    assets,receipt=build()
    if args.validate_only:
        print(json.dumps(receipt,indent=2));return
    dest=args.output_dir.resolve()
    if dest.exists() and any(dest.iterdir()):
        parser.error("REVIEW HOLD: nonempty target directory; refusing overwrite")
    dest.mkdir(parents=True,exist_ok=True)
    for name,blob in assets.items():(dest/name).write_bytes(blob)
    (dest/MANIFEST).write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2))

if __name__=="__main__":main()
