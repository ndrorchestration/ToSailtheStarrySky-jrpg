#!/usr/bin/env python3
"""Deterministic noncanonical Aureate V4 geodesic bridge + curved quarters GLBs.

Models two separate static meshes for a SHARED review-only pivot. Does not
touch production, original saved maps, gameplay, pressure seals or Starbourne.
Review dimensions (centimeters) are not canon. Source axis +X forward, +Z up.
"""
from __future__ import annotations
import argparse, hashlib, json, math, sys
from pathlib import Path

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
from build_aureate_body_review import Surface, bridge_dome, encode_glb, STATUS

FILES=("AureateWake_CoupledBridge_Geodesic_REVIEW.glb",
       "AureateWake_CurvedLivingQuarters_REVIEW.glb")
MANIFEST="CoupledHabitationLookdevManifest.json"
PROVENANCE="AUREATE_V4_NONCANONICAL_COUPLED_HABITATION_20261104"
DOME_ORIGIN_CM=(170.0,0.0,133.0)
PIVOT_ORIGIN_CM=(40.0,0.0,72.0)
GEOMETRY_ONLY=True

def quarters_surfaces():
    ivory, gold, glazing=(Surface(n) for n in
        ("PorcelainCurvedQuarters","BronzeLoadPath","BlueInsetCabinGlazing"))
    stations=[(-185,17,20),(-160,33,28),(-110,50,29),(-55,55,30),
              (25,58,30),(95,56,29),(165,53,27),(220,36,23),(248,12,14)]
    # Loft a rounded continuous skin rather than one rectangular cuboid.
    rings=[]
    n=28
    for x,width,height in stations:
        row=[]
        for j in range(n):
            a=2*math.pi*j/n
            c=math.cos(a)
            row.append((x,width*math.sin(a),54+height*(c if c>=0 else .64*c)))
        rings.append(row)
    for before,after in zip(rings,rings[1:]):
        for j in range(n):
            k=(j+1)%n
            ivory.quad(before[j],after[j],after[k],before[k])
    for ring in (rings[0],rings[-1]):
        x=ring[0][0]
        for j in range(n):
            ivory.tri((x,0,54),ring[j],ring[(j+1)%n])
    # Segmented brass ribs and two long coherent shoulder sweeps.
    for row in rings[1:-1]:
        for j in range(n):
            k=(j+1)%n
            gold.tube(row[j],row[k],.58,6,False)
    for side in (-1,1):
        for i in range(len(stations)-1):
            x0,w0,h0=stations[i];x1,w1,h1=stations[i+1]
            gold.tube((x0,side*w0,56),(x1,side*w1,56),1.45,8,False)
            gold.tube((x0,side*w0*.71,54+h0*.72),
                      (x1,side*w1*.71,54+h1*.72),.8,6,False)
        # Blue insets with individual frames, still NOT pressure windows.
        for x,width in ((-120,48),(-50,55),(30,58),(105,55)):
            yy=side*(width+2.2)
            glazing.quad((x-10,yy,54),(x+10,yy,54),
                         (x+10,yy,68),(x-10,yy,68))
            for a,b in (((x-10,yy,54),(x+10,yy,54)),
                        ((x+10,yy,54),(x+10,yy,68)),
                        ((x+10,yy,68),(x-10,yy,68)),
                        ((x-10,yy,68),(x-10,yy,54))):
                gold.tube(a,b,1.05,6,False)
    # Visual collar beneath the separate bridge dome, not sealed or structural.
    for j in range(48):
        a=j*math.tau/48; b=(j+1)*math.tau/48
        p=(170+91*math.cos(a),54*math.sin(a),78)
        q=(170+91*math.cos(b),54*math.sin(b),78)
        gold.tube(p,q,1.45,8,False)
    return [ivory,gold,glazing]

DOME_MATERIALS=[
 {"name":"V4Review_TurquoiseGlass_NOT_PRESSURE_RATED","alphaMode":"BLEND","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.15,.54,.68,.27],"metallicFactor":.2,"roughnessFactor":.15}},
 {"name":"V4Review_BrassGeodesicStruts","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.78,.51,.20,1],"metallicFactor":.82,"roughnessFactor":.26}},
 {"name":"V4Review_DomeDockingCollar_NOT_SEALED","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.09,.18,.25,1],"metallicFactor":.5,"roughnessFactor":.42}}
]
QUARTERS_MATERIALS=[
 {"name":"V4Review_PearlCurvedCanopy","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.61,.70,.73,1],"metallicFactor":.32,"roughnessFactor":.36}},
 {"name":"V4Review_ContinuousBronzeRibs","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.82,.52,.19,1],"metallicFactor":.83,"roughnessFactor":.3}},
 {"name":"V4Review_BlueInsetWindows_NOT_PRESSURE_RATED","doubleSided":True,
  "pbrMetallicRoughness":{"baseColorFactor":[.035,.36,.52,1],"metallicFactor":.45,"roughnessFactor":.2}}
]
def payloads():
    surfaces=[bridge_dome(),quarters_surfaces()]
    for group in surfaces:
        if len(group)!=3 or not all(x.indices for x in group):
            raise ValueError("Expected three populated design sections")
        for section in group:
            if len(section.indices)%3 or not all(math.isfinite(z) for p in section.pos for z in p):
                raise ValueError("Invalid triangulated geometry")
    return {FILES[0]:encode_glb("CoupledGeodesicBridgeReview",surfaces[0],DOME_MATERIALS),
            FILES[1]:encode_glb("CoupledQuartersReview",surfaces[1],QUARTERS_MATERIALS)}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",type=Path,required=True)
    flag=parser.add_mutually_exclusive_group(required=True)
    flag.add_argument("--build",action="store_true")
    flag.add_argument("--verify",action="store_true")
    a=parser.parse_args()
    folder=a.output_dir.resolve()
    if a.build:folder.mkdir(parents=True,exist_ok=True)
    if not folder.is_dir():raise FileNotFoundError("Review output folder missing")
    blobs=payloads()
    manifest={"authority":PROVENANCE,"source_status":STATUS,
        "content_sha256":{name:hashlib.sha256(data).hexdigest() for name,data in blobs.items()},
        "bridge_actor_origin_cm":list(DOME_ORIGIN_CM),
        "pivot_origin_cm":list(PIVOT_ORIGIN_CM),
        "geometry_units":"centimeters_in_source_meters_in_gltf",
        "shared_pivot_required":True,"pressure_or_cabin_seal_verified":False,
        "physical_clearance_verified":False,"creator_art_approved":False,
        "production_content_modified":False,"starbourne_player_unlocked":False}
    blobs[MANIFEST]=(json.dumps(manifest,sort_keys=True,indent=2)+"\n").encode("utf8")
    for name,data in blobs.items():
        p=folder/name
        if p.exists():
            if p.read_bytes()!=data:raise RuntimeError("Existing review evidence drift: "+str(p))
        elif a.build:
            p.write_bytes(data)
        else:raise FileNotFoundError(p)
    print(json.dumps({"state":"DETERMINISTIC_HABITATION_SOURCE_PASS_NOT_NATIVE",
        "output_dir":str(folder),**manifest},sort_keys=True))
if __name__=="__main__":main()
