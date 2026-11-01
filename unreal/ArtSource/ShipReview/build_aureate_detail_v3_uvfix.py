#!/usr/bin/env python3
"""Review-only UV tangent repair for original V3 GLBs without changing V3 bytes.

The original fairing/interior files, geometry, normals, materials, and gameplay
are untouched. These are distinct GLBs and paths requiring new Unreal review.
Each source triangle is planar-projected along its dominant face-normal axis
instead of mapping every triangle to X/Z, which collapsed UVs on X/Y/Z faces.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import build_aureate_detail_v3 as v3
from build_aureate_body_review import encode_glb

FILES = (
    "AureateWake_RootFairing_V3_UVFIX_REVIEW.glb",
    "AureateWake_BridgeInterior_V3_UVFIX_REVIEW.glb",
)
MANIFEST = "AureateWake_DetailV3_UVFix_Manifest.json"
STAGE = "NONCANONICAL_V3_UV_TANGENT_REPAIR_NOT_ART_APPROVED"
UV_TILING = 20.0  # 1 glTF metre = 20 UV units; adequate for fine brass trim.

class UVFixHold(ValueError):
    pass

def uv_area(uv0, uv1, uv2):
    return ((uv1[0]-uv0[0])*(uv2[1]-uv0[1])
            -(uv1[1]-uv0[1])*(uv2[0]-uv0[0]))

def reproject(surface):
    if len(surface.pos) != len(surface.normal) or len(surface.pos)!=len(surface.uv):
        raise UVFixHold("Source attribute counts inconsistent")
    if len(surface.indices)%3 or surface.indices!=list(range(len(surface.pos))):
        raise UVFixHold("Per-triangle duplicated vertices expected; no shared UV rewrite")
    for i in range(0,len(surface.pos),3):
        pts=surface.pos[i:i+3]
        normal=surface.normal[i]
        if any(n!=normal for n in surface.normal[i:i+3]):
            raise UVFixHold("Unexpected mixed facet normals")
        if not all(math.isfinite(x) for row in pts for x in row):
            raise UVFixHold("Nonfinite source coordinate")
        major=max(range(3),key=lambda j:abs(normal[j]))
        # Cyclic axes ensure the UV plane has maximal projection area
        # for the triangle's face. Preserve positive UV orientation.
        axes=((1,2),(2,0),(0,1))[major]
        uv=[(p[axes[0]]*UV_TILING,p[axes[1]]*UV_TILING)
            for p in pts]
        if normal[major]<0:
            uv=[(-x,y) for x,y in uv]
        area=uv_area(*uv)
        if not math.isfinite(area) or area<=1e-6:
            raise UVFixHold("Missing or collapsed per-face UV tangent basis")
        surface.uv[i:i+3]=uv
    return surface

def surfaces():
    return {
        FILES[0]:[reproject(s) for s in v3.fairing_surfaces()],
        FILES[1]:[reproject(s) for s in v3.interior_surfaces()],
    }

def payloads():
    pairs=surfaces()
    return {
        FILES[0]:encode_glb("RootFairingUVFix",pairs[FILES[0]],v3.FAIRING_MATS),
        FILES[1]:encode_glb("BridgeInteriorUVFix",pairs[FILES[1]],v3.INTERIOR_MATS),
    }

def manifest(blobs):
    return {
        "authority":v3.STATUS,
        "stage":STAGE,
        "original_creator_approved_image_sha256":v3.ART_SHA,
        "origin_unchanged_v3_sha256":v3.receipt(v3.payloads())["sha256"],
        "uv_tiling":UV_TILING,
        "uv_basis":"per-triangle dominant normal projection in glTF metres",
        "sha256":{name:hashlib.sha256(data).hexdigest() for name,data in blobs.items()},
        "native_import":"NOT_VERIFIED",
        "native_tangent_warning_fix":"NOT_VERIFIED",
        "creator_model_approval":False,
        "gameplay_modified":False,
        "orbiter_authorized":False,
    }

def build_or_verify(folder:Path,build:bool):
    folder=folder.resolve()
    if build:folder.mkdir(parents=True,exist_ok=True)
    if not folder.is_dir() or folder.is_symlink():
        raise UVFixHold("Invalid review output directory")
    data=payloads()
    receipt=manifest(data)
    output={**data,MANIFEST:(json.dumps(receipt,indent=2,sort_keys=True)+"\n").encode()}
    extra={p.name for p in folder.iterdir()}-set(output)
    if extra:raise UVFixHold("Unexpected contents in review folder")
    for name,blob in output.items():
        p=folder/name
        if p.exists():
            if p.is_symlink() or not p.is_file() or p.read_bytes()!=blob:
                raise UVFixHold("Refusing to overwrite review asset "+name)
        elif build:p.write_bytes(blob)
        else:raise UVFixHold("Missing exact review asset "+name)
    return receipt

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build",action="store_true")
    mode.add_argument("--verify",action="store_true")
    args=p.parse_args(argv)
    print(json.dumps(build_or_verify(args.output_dir,args.build),indent=2,sort_keys=True))

if __name__=="__main__":main()
