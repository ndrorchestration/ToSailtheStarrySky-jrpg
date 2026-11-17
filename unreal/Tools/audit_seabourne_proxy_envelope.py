"""Bounded, source-locked AABB analysis of four BASIC-CUBE Seabourne wind sails.

This does NOT analyze the authored wing GLB, real Unreal StaticMesh bounds, hinge
sweep, continuous trim, hull art, bridge art, moving obstacles, dock clearance,
wind force, animation or native gameplay. Proxy END-POSE yaw samples only.
"""
from __future__ import annotations
import argparse
import json
import math
import re
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
CPP=HERE/"Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
H=HERE/"Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h"
YAW_SAMPLES=tuple(range(-35,36,5))
HALF_CUBE_CM=50.0

def require(value,reason):
    if not value:
        raise ValueError("SEABOURNE_PROXY_AABB_HOLD: "+reason)

def lock_source():
    source=CPP.read_text(encoding="utf-8")
    hdr=H.read_text(encoding="utf-8")
    checks=[
        "bool bUseSeabourneWindSailReview = false;",
        "FVector(2.8f, 1.25f, 0.05f)",
        "const float Z = bAuthoredRootPivot ? 228.f : 365.f;",
        "return FTransform(FRotator(98.f, TrimDegrees, 0.f),",
        "!FMath::IsFinite(Degrees) || FMath::Abs(Degrees) > 35.f",
        "bSeabourneWindSailPoseActive = false;",
        "const FVector HullAnchor(Root.X, Side * 73.f, 18.f);",
        "if (Support) Support->SetVisibility(false);",
        "Hull->SetRelativeScale3D(FVector(8.f, 1.5f, .65f));",
        "ForwardBridge->SetRelativeLocation(FVector(240.f, 0.f, 95.f));",
        "ForwardBridge->SetRelativeScale3D(FVector(2.1f, 1.1f, 1.1f));",
    ]
    alltext=source+"\n"+hdr
    for token in checks:
        require(token in alltext,"source contract drift: "+token)
    mat=re.search(r"static constexpr float StationsX\[4\]\s*=\s*\{([^}]+)\}",source)
    require(mat is not None,"four dorsal stations missing")
    vals=[float(s.strip().removesuffix("f")) for s in mat.group(1).split(",")]
    require(len(vals)==4 and all(math.isfinite(x) for x in vals),"station count")
    require(all(vals[i]>vals[i+1] for i in range(3)),"fore/aft ordering")
    # These source values represent placeholder cube preview geometry ONLY.
    return tuple(vals)

def aabb(center,extents):
    return tuple((float(center[i]-extents[i]),float(center[i]+extents[i])) for i in range(3))

def sail(station,yaw_deg,z_cm=365.0):
    """Unreal-style yaw Z + pitch Y acting on 100cm cube scaled 2.8/1.25/.05.
    Explicit order assumption: yaw then pitch, no roll. Not a native readback.
    """
    p=math.radians(98.0)
    y=math.radians(yaw_deg)
    ex=(140.0,62.5,2.5)
    # Local X (length) / Y (width) / Z (thickness), world abs half extents.
    horiz_cos=abs(math.cos(p))
    horiz_sin=abs(math.sin(p))
    cy,sy=abs(math.cos(y)),abs(math.sin(y))
    ext=(
        ex[0]*horiz_cos*cy+ex[1]*sy+ex[2]*horiz_sin*cy,
        ex[0]*horiz_cos*sy+ex[1]*cy+ex[2]*horiz_sin*sy,
        ex[0]*horiz_sin+ex[2]*horiz_cos,
    )
    return aabb((station,0.,z_cm),ext)

def separation(first,second):
    """Zero for touching/intersecting proxy boxes; else shortest AABB distance."""
    gaps=[]
    for (a,b),(c,d) in zip(first,second):
        gaps.append(max(0.,c-b,a-d))
    return math.sqrt(sum(v*v for v in gaps))

def analyze(stations, bridge_z=95., samples=YAW_SAMPLES):
    require(len(stations)==4 and len(set(stations))==4,"exactly four distinct stations")
    require(samples and all(math.isfinite(x) and abs(x)<=35 for x in samples),
            "sampled bounds stay within provisional review control")
    hull=aabb((0.,0.,0.),(400.,75.,32.5))
    bridge=aabb((240.,0.,bridge_z),(105.,55.,55.))
    hydrofoils=[
        aabb((0.,side*80.,-140.),(105.,37.5,5.)) for side in (-1.,1.)
    ]
    results=[]
    poses=[[sail(x,deg) for deg in samples] for x in stations]
    for i in range(4):
        for n,pose in enumerate(poses[i]):
            for name,obstacle in (("proxy-hull",hull),("proxy-bridge",bridge),
                                  ("proxy-hydrofoil-1",hydrofoils[0]),
                                  ("proxy-hydrofoil-2",hydrofoils[1])):
                gap=separation(pose,obstacle)
                results.append((gap,f"wing-{i+1} / {name} / yaw={samples[n]}"))
        for j in range(i+1,4):
            for x,one in enumerate(poses[i]):
                for y,two in enumerate(poses[j]):
                    gap=separation(one,two)
                    results.append((gap,f"wing-{i+1} / wing-{j+1} / "
                                        f"yaw={samples[x]},{samples[y]}"))
    min_gap,critical=min(results,key=lambda p:p[0])
    require(min_gap>0.,"proxy box overlap or contact at "+critical)
    return {
        "status":"SOURCE_LOCKED_BASIC_CUBE_ENDPOINT_YAW_SAMPLES_AABB_CLEAR",
        "stations_cm":list(stations),
        "tested_wings":4,
        "yaw_samples_degrees":list(samples),
        "evaluated_box_pairs":len(results),
        "minimum_proxy_aabb_gap_cm":round(min_gap,3),
        "critical_pair":critical,
        "actual_mesh_geometry_evaluated":False,
        "actual_native_unreal_evaluated":False,
        "swept_deployment_or_continuous_yaw_verified":False,
        "verified_collision_clearance":False,
        "wind_propulsion_verified":False,
        "creator_approved":False
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check",action="store_true",required=True)
    args=p.parse_args()
    print(json.dumps(analyze(lock_source()),sort_keys=True,indent=2))

if __name__=="__main__":
    main()
