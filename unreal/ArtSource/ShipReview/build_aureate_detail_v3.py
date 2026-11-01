#!/usr/bin/env python3
"""Deterministic Aureate Wake V3 hinge fairing + habitable-looking bridge study.

Independent GLB assets for RESTRICTED review paths; neither physical pressure
protection nor any creator-approved model, story event or game system.
UE centimetres X forward Z up -> glTF metres Y up. No external dependencies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from build_aureate_body_review import Surface, encode_glb, STATUS

ART_SHA = "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13"
FAIRING = "AureateWake_RootFairing_V3_REVIEW.glb"
INTERIOR = "AureateWake_BridgeInterior_V3_REVIEW.glb"
MANIFEST = "AureateWake_DetailV3_Manifest.json"
FILES = (FAIRING, INTERIOR)
PROVENANCE = "NONCANONICAL_V3_HINGE_AND_BRIDGE_DETAIL_PREVIEW_ONLY"

def ring(surface:Surface,x:float,cy:float,cz:float,ry:float,rz:float,n=16):
    return [(x, cy+ry*math.cos(2*math.pi*i/n),
                cz+rz*math.sin(2*math.pi*i/n)) for i in range(n)]

def connect(surface:Surface,a,b, reverse=False):
    if len(a)!=len(b):raise ValueError("Incompatible mesh rings")
    for i in range(len(a)):
        j=(i+1)%len(a)
        if reverse:surface.quad(a[i],a[j],b[j],b[i])
        else:surface.quad(a[j],a[i],b[i],b[j])

def fairing_surfaces():
    """A 52cm tapered ivory sleeve, gold edge hoops, navy ball-seat/blue core.

    Origin at hull-side anchor, +X points toward the existing reviewed wing
    root. Four separate mesh actors will be scaled by link_length/52.
    """
    ivory,gold,navy,cyan=(Surface(x) for x in (
        "IvoryJointShroud","BrassJointHoops","DeepNavyActuator","BlueResonanceTrace"))
    profiles=(
        (-3.0,22.0,17.0),
        (8.0,22.0,18.5),
        (22.0,18.5,15.5),
        (38.0,13.0,11.0),
        (51.0,12.5,10.0),
    )
    rings=[ring(ivory,x,0,0,y,z) for x,y,z in profiles]
    for a,b in zip(rings,rings[1:]):connect(ivory,a,b)
    # An open bore remains visual-only; no seal/collision claim.
    inner0=ring(navy,-3.0,0,0,8.0,7.0)
    inner1=ring(navy,51.0,0,0,8.0,7.0)
    connect(navy,inner0,inner1,True)
    connect(ivory,inner0,rings[0],True)
    connect(ivory,rings[-1],inner1)
    for x,ry,rz in ((0,22.5,18),(20,19,16),(49,13,11)):
        points=ring(gold,x,0,0,ry,rz)
        for j in range(len(points)):
            gold.tube(points[j],points[(j+1)%len(points)],1.4,6)
    navy.tube((7,0,-18),(40,0,-9),3.2,8)
    navy.tube((7,0,18),(40,0,9),3.2,8)
    for y in (-14,14):
        cyan.tube((9,y,0),(37,y*.67,0),1.5,8)
    return [ivory,gold,navy,cyan]

def interior_surfaces():
    """Local to current geodesic dome, near its bottom at local Z=-60."""
    navy,gold,ivory,cyan=(Surface(x) for x in (
        "NavyWalkableLookingFloor","BrassInteriorStructures",
        "IvorySeatsAndPanels","CyanNavigationDisplays"))
    navy.block(-79,78,-43,43,-56,-52)
    # Raised dark center bridge aisle with inset accent trim.
    navy.block(-69,48,-11,11,-51,-48)
    for y in (-44,44):
        gold.tube((-75,y,-51),(70,y,-51),1.7,8)
    for y in (-12,12):
        gold.tube((-66,y,-47),(44,y,-47),.9,6)
    # Forward panoramic helm that follows the glass footprint.
    ivory.block(43,67,-35,35,-48,-35)
    navy.block(61,72,-33,33,-34,-16)
    cyan.quad((70,-29,-14),(70,29,-14),(69,26,-4),(69,-26,-4))
    for side in (-1,1):
        # Side displays and captain station.
        lo,hi=sorted((side*17,side*38))
        navy.block(5,34,lo,hi,-45,-31)
        cyan.quad((9,side*20,-30),(30,side*20,-30),
                  (30,side*37,-29),(9,side*37,-29))
        # Captain and officer seats, facing +X.
        y=side*24
        navy.block(-30,-12,y-9,y+9,-47,-35)
        ivory.block(-33,-26,y-10,y+10,-34,-8)
        ivory.block(-27,-9,y-9,y+9,-32,-26)
        gold.tube((-26,y-11,-47),(-26,y-11,-8),1.5,6)
        gold.tube((-26,y+11,-47),(-26,y+11,-8),1.5,6)
        # Interior brass rib braces, not a pressure boundary.
        gold.tube((-67,side*41,-50),(-36,side*41,18),1.3,8)
        gold.tube((32,side*38,-49),(57,side*25,8),1.2,8)
    # Chart table and resonance navigation prism, purely cosmetic.
    navy.block(-10,13,-12,12,-47,-37)
    ivory.block(-17,20,-22,22,-36,-31)
    cyan.block(-9,12,-12,12,-30,-28)
    gold.tube((-17,-22,-30),(20,-22,-30),1.1,6)
    gold.tube((-17,22,-30),(20,22,-30),1.1,6)
    for x in (-55,-42):
        cyan.block(x,x+5,-36,-32,-52,-49)
        cyan.block(x,x+5,32,36,-52,-49)
    return [navy,gold,ivory,cyan]

def mat(name,rgba,metal,rough,*,emissive=None,blend=False):
    out={"name":name+"_REVIEW","pbrMetallicRoughness":{
         "baseColorFactor":rgba,"metallicFactor":metal,
         "roughnessFactor":rough},"doubleSided":True}
    if emissive:out["emissiveFactor"]=emissive
    if blend:out["alphaMode"]="BLEND"
    return out

FAIRING_MATS=[
    mat("IvoryPearlJoint",[.93,.88,.76,1],.31,.27),
    mat("WarmBrassRing",[.84,.52,.19,1],.88,.25),
    mat("BlueBlackActuator",[.025,.07,.14,1],.62,.32),
    mat("CyanResonanceGuide",[.09,.65,.94,1],.26,.24,emissive=[.03,.24,.52]),
]
INTERIOR_MATS=[
    mat("NavyCrewDeck",[.025,.09,.16,1],.31,.46),
    mat("BrassBridgeRibs",[.87,.54,.19,1],.82,.28),
    mat("IvoryHelmSeating",[.88,.85,.72,1],.19,.4),
    mat("CyanChartPanels",[.05,.50,.9,1],.17,.22,emissive=[.04,.26,.54]),
]

def payloads() -> dict[str,bytes]:
    return {FAIRING:encode_glb("RootFairing",fairing_surfaces(),FAIRING_MATS),
            INTERIOR:encode_glb("BridgeInterior",interior_surfaces(),INTERIOR_MATS)}

def receipt(blobs):
    return {
        "status":STATUS,
        "stage":PROVENANCE,
        "original_approved_image_sha256":ART_SHA,
        "units":"glTF meters, Unreal authored centimetres",
        "axes":"Unreal X-forward Z-up to glTF Y-up",
        "fairing_local_x_length_cm":54.0,
        "material_sections_each":4,
        "sha256":{name:hashlib.sha256(data).hexdigest() for name,data in blobs.items()},
        "requires_native_review":True,
        "actual_unreal_import":"NOT_ESTABLISHED",
        "creator_model_approval":False,
        "gameplay_modified":False,
        "orbiter_authorized":False,
    }

def build_or_verify(folder:Path,build:bool):
    folder=folder.resolve()
    if build:folder.mkdir(parents=True,exist_ok=True)
    if not folder.is_dir():raise ValueError("Review folder missing")
    blobs=payloads(); r=receipt(blobs)
    files={**blobs, MANIFEST:(json.dumps(r,indent=2,sort_keys=True)+"\n").encode("utf-8")}
    unknown={p.name for p in folder.iterdir()}-set(files)
    if unknown:raise ValueError("Unexpected files in review folder: "+repr(unknown))
    for name,bytes_ in files.items():
        file=folder/name
        if file.exists():
            if file.is_symlink() or not file.is_file() or file.read_bytes()!=bytes_:
                raise ValueError("Refusing to replace changed review output: "+name)
        elif build:file.write_bytes(bytes_)
        else:raise ValueError("Missing review output: "+name)
    return r

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-dir",required=True,type=Path)
    m=p.add_mutually_exclusive_group(required=True)
    m.add_argument("--build",action="store_true")
    m.add_argument("--verify",action="store_true")
    args=p.parse_args(argv)
    print(json.dumps(build_or_verify(args.output_dir,args.build),indent=2,sort_keys=True))

if __name__=="__main__":main()
