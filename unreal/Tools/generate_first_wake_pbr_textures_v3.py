#!/usr/bin/env python3
"""Original, source-locked procedural PBR review textures for First Wake.

Pure Python stdlib; deterministic PNG byte and SHA-256 outputs across Windows
and hosted Linux. Source *lookdev*, not final photogrammetric/AAA materials.
No remote image/texture licenses, Unreal changes, or production map mutations.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from math import isqrt
from pathlib import Path
import struct
import zlib

OUT=Path(__file__).resolve().parents[1]/"ArtSource/FirstWakeMaterialsV3"
DIM=512
ROLES={
    "quay_stone":    ((69,84,91),205,0,"flagstone",6),
    "harbor_plaster":((157,146,125),217,0,"plaster",11),
    "warm_roof":     ((136,62,46),223,0,"terracotta",13),
    "dock_timber":   ((91,65,47),220,0,"timber",17),
    "patina_metal":  ((46,104,105),132,205,"oxidized_metal",19),
    "warm_stone_trim":((170,141,115),202,0,"flagstone",23),
    "blue_green_glass":((32,113,126),45,4,"glass",29),
    "dark_copper":   ((84,46,31),100,218,"oxidized_metal",31),
    "sea_foam":      ((148,192,181),107,0,"foam",37),
    "ochre_canvas":  ((176,113,65),218,0,"canvas",41),
}
CHANNELS=("BaseColor","Normal","Roughness")
MASK=(1<<32)-1

def clamp(v,lo=0,hi=255):
    return max(lo,min(hi,int(v)))

def hashed(x,y,seed):
    z=((x*0x9E3779B1)^(y*0x85EBCA77)^(seed*0xC2B2AE3D))&MASK
    z^=z>>16
    z=(z*0x7FEB352D)&MASK
    z^=z>>15
    z=(z*0x846CA68B)&MASK
    return (z^(z>>16))&255

def noise(x,y,step,seed):
    # Integer bilinear interpolation: same image bytes on all Python builds.
    gx,gy=x//step,y//step
    fx,fy=x%step,y%step
    ax=hashed(gx,gy,seed)*(step-fx)+hashed(gx+1,gy,seed)*fx
    bx=hashed(gx,gy+1,seed)*(step-fx)+hashed(gx+1,gy+1,seed)*fx
    return (ax*(step-fy)+bx*fy)//(step*step)

def pattern(x,y,style):
    if style=="flagstone":
        row=y//45
        tx=(x+(row%2)*23)%63
        ty=y%45
        joint=min(tx,63-tx,ty,45-ty)
        return (-75 if joint<=2 else 0),((x+(row%2)*23)//63+row*43)
    if style=="terracotta":
        row=y//32
        tx=(x+(row%2)*15)%32
        joint=min(tx,32-tx,y%32,32-y%32)
        return (-57 if joint<=2 else 0),((x+(row%2)*15)//32+row*47)
    if style=="timber":
        plank=x%54
        seam=min(plank,54-plank)
        knots=-(max(0,19-abs((x%113)-57))//3)
        grain=(hashed(x//8,y//86,72)-128)//7
        return (-72 if seam<=2 else 0)+knots+grain,x//54
    if style=="canvas":
        return ((24 if x%8==0 or y%8==0 else -3)),0
    if style=="oxidized_metal":
        return ((noise(x,y,31,91)-128)//3),0
    if style=="glass":
        return ((noise(x,y,70,94)-128)//6),0
    if style=="foam":
        return ((noise(x,y,19,79)-128)//4),0
    return 0,0

def bytes_for_role(name):
    if name not in ROLES:raise ValueError("Unknown material role "+name)
    color,rough,metal,style,seed=ROLES[name]
    pixels=bytearray(DIM*DIM*3)
    heights=bytearray(DIM*DIM)
    roughness=bytearray(DIM*DIM)
    for y in range(DIM):
        for x in range(DIM):
            idx=y*DIM+x
            large=noise(x,y,128,seed)-128
            small=noise(x,y,13,seed+72)-128
            edge,cell=pattern(x,y,style)
            variation=(large//4+small//9+edge+
                       (hashed(cell,seed,17)-128)//8)
            if style=="plaster":
                variation+=((noise(x,y,53,seed+8)-128)//3)
            if style=="oxidized_metal":
                variation+=((noise(x,y,89,seed+45)-128)//3)
            heights[idx]=clamp(128+variation//2)
            scale=(255+variation)
            offset=idx*3
            for c in range(3):
                pixels[offset+c]=clamp(color[c]*scale//255)
            roughness[idx]=clamp(rough+small//8+large//11+(-edge//4))
    normals=bytearray(DIM*DIM*3)
    for y in range(DIM):
        up=max(0,y-1);down=min(DIM-1,y+1)
        for x in range(DIM):
            left=max(0,x-1);right=min(DIM-1,x+1)
            idx=y*DIM+x
            dx=int(heights[y*DIM+right])-int(heights[y*DIM+left])
            dy=int(heights[down*DIM+x])-int(heights[up*DIM+x])
            nx=-dx*3;ny=-dy*3;nz=230
            length=max(1,isqrt(nx*nx+ny*ny+nz*nz))
            off=idx*3
            normals[off]=clamp(128+(nx*127)//length)
            normals[off+1]=clamp(128+(ny*127)//length)
            normals[off+2]=clamp(128+(nz*127)//length)
    return {"BaseColor":bytes(pixels),"Normal":bytes(normals),
            "Roughness":bytes(roughness)}

def chunk(kind,data):
    return struct.pack(">I",len(data))+kind+data+struct.pack(">I",zlib.crc32(kind+data))

def encode_png(rgb,channels):
    if channels not in (1,3):raise ValueError("Only grayscale/RGB source maps")
    if len(rgb)!=DIM*DIM*channels:
        raise ValueError("Invalid number of texture pixels")
    color_type=2 if channels==3 else 0
    ihdr=struct.pack(">IIBBBBB",DIM,DIM,8,color_type,0,0,0)
    scan=b"".join(b"\x00"+rgb[y*DIM*channels:(y+1)*DIM*channels]
                  for y in range(DIM))
    return (b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",ihdr)+
            chunk(b"IDAT",zlib.compress(scan,7))+chunk(b"IEND",b""))

def inventory():
    rows=[]
    blobs={}
    for name in sorted(ROLES):
        source=bytes_for_role(name)
        for channel in CHANNELS:
            filename=f"TX_FWV3_{name}_{channel}.png"
            data=encode_png(source[channel],1 if channel=="Roughness" else 3)
            blobs[filename]=data
            rows.append({"name":filename,"material":name,"channel":channel,
                         "sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data),
                         "dimensions":[DIM,DIM],
                         "status":"SOURCE_ONLY_PBR_TEXTURE_NOT_NATIVE_IMPORTED"})
    return {"version":3,"status":"SOURCE_TEXTURES_NOT_NATIVE_RENDERED",
            "resolution":[DIM,DIM],"roles":len(ROLES),"textures":rows,
            "asset_authority":"CUSTOM_PROCEDURAL_REVIEW_ONLY_NOT_APPROVED",
            "normal_authority":"SOURCE_TANGENT_PROXY_NOT_VERIFIED_NATIVE_TANGENT_SPACE",
            "contains_licensed_assets":False},blobs

def save():
    manifest,blobs=inventory()
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/"manifest.json"
    if target.exists() or any((OUT/name).exists() for name in blobs):
        raise RuntimeError("HOLD: previous generated PBR output exists")
    for name,blob in blobs.items():
        with (OUT/name).open("xb") as out:out.write(blob)
    with target.open("x",encoding="utf-8") as out:
        json.dump(manifest,out,indent=2,sort_keys=True)
    return manifest

def verify():
    file=OUT/"manifest.json"
    if not file.is_file():raise RuntimeError("HOLD: missing source material manifest")
    expected,blobs=inventory()
    actual=json.loads(file.read_text(encoding="utf-8"))
    if actual!=expected:raise RuntimeError("HOLD: source material metadata drift")
    for name,blob in blobs.items():
        disk=OUT/name
        if not disk.is_file() or disk.read_bytes()!=blob:
            raise RuntimeError("HOLD: source material texture bytes drift: "+name)
    return {"status":"SOURCE_PBR_TEXTURE_SHA256_PASS_NOT_NATIVE",
            "texture_count":len(blobs),"roles":len(ROLES),
            "source_files_unchanged":True}

def main():
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--generate",action="store_true")
    g.add_argument("--verify",action="store_true")
    a=p.parse_args()
    result=save() if a.generate else verify()
    print(json.dumps({k:v for k,v in result.items() if k!="textures"},sort_keys=True))
if __name__=="__main__":
    main()
