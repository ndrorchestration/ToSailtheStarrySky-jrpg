#!/usr/bin/env python3
"""Read-only Skyborne composite plan matching the root-pivoted C++ preview pose.

Four dragonfly wings, four separate visual supports; NO mode transitions,
Orbiter, story progression, water authority, production scene binding or art
approval. Local geometry in Unreal centimetres. Does not import or edit assets.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import math
from pathlib import Path

CPP = Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky" / "Private" / "AureateWakePreviewActor.cpp"
MAP = "/Game/TSTSS/Review/V2_Skyborne_Assembly_V1"
REFERENCE_SHA256 = "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13"
WING_PATH = ("/Game/TSTSS/Review/ShipArt/WingCandidateV2/AureateWake_Wing_Lookdev/"
             "StaticMeshes/AureateWake_Wing_Lookdev.AureateWake_Wing_Lookdev")
SUPPORT_PATH = ("/Game/TSTSS/Review/ShipArt/RootSupportCandidateV1/"
                "AureateWake_RootSupport_Lookdev/StaticMeshes/"
                "AureateWake_RootSupport_Lookdev.AureateWake_RootSupport_Lookdev")
WING_CANDIDATE_COUNT = 4
SUPPORT_CANDIDATE_COUNT = 4
HULL_REVIEW_HEIGHT_CM = 140

@dataclass(frozen=True)
class Wing:
    id: int
    side: int
    forward: bool
    location_cm: tuple[float,float,float]
    pitch_yaw_roll_deg: tuple[float,float,float]
    scale: tuple[float,float,float] = (1,1,1)

@dataclass(frozen=True)
class Support:
    id: int
    location_cm: tuple[float,float,float]
    end_cm: tuple[float,float,float]
    scale: tuple[float,float,float]
    length_cm: float

@dataclass(frozen=True)
class Camera:
    name: str
    location_cm: tuple[int,int,int]
    target_cm: tuple[int,int,int]

CAMERAS=(
    Camera("01_ThreeQuarter",(-880,-1550,810),(0,0,185)),
    Camera("02_PortSide",(-130,-1500,450),(0,0,180)),
    Camera("03_Dorsal",(-250,-650,1600),(0,0,180)),
    Camera("04_BowPerspective",(1120,-1350,540),(60,0,180)),
)

def validate_cpp_contract():
    """Hold if the actor's C++ source diverges from this bounded pose."""
    s=CPP.read_text(encoding="utf-8")
    begin=s.index("FTransform AAureateWakePreviewActor::RootPivotedWingPose(")
    end=s.index("FTransform AAureateWakePreviewActor::WingPoseForMesh(",begin)
    block=s[begin:end]
    for token in (
        "WingIndex < 2", "WingIndex % 2 == 0 ? -1.f : 1.f",
        "bForward ? 155.f : -180.f", "Side * 112.f",
        "Position(RootX, RootY, 48.f)",
        "Side * (bForward ? 80.f : 100.f), Side * 7.f",
        "case EAureateWakeForm::Skyborne:",
    ):
        if token not in block:
            raise ValueError("Review pose changed in C++: "+token)
    start=s.index("void AAureateWakePreviewActor::UpdateRootSupportTransforms()")
    stop=s.index("FTransform AAureateWakePreviewActor::WingPose(",start)
    supports=s[start:stop]
    for token in ("Side * 73.f, 18.f","Length / 100.f","FRotationMatrix::MakeFromX(Link)"):
        if token not in supports:
            raise ValueError("Root support C++ contract changed: "+token)
    if not s.count("WingRootSupports.Add(Support);")==1:
        raise ValueError("Structural support count source changed")

def build_plan():
    validate_cpp_contract()
    wings=[];supports=[]
    for i in range(4):
        side=-1 if i%2==0 else 1
        forward=i<2
        x=155 if forward else -180
        root=(float(x),float(side*112),float(HULL_REVIEW_HEIGHT_CM+48))
        rotation=(0.0,float(side*(80 if forward else 100)),float(side*7))
        wings.append(Wing(i+1,side,forward,root,rotation))
        start=(float(x),float(side*73),float(HULL_REVIEW_HEIGHT_CM+18))
        length=math.dist(start,root)
        supports.append(Support(i+1,start,root,(length/100,1.,1.),length))
    if len(wings)!=4 or len(supports)!=4 or len(CAMERAS)!=4:
        raise ValueError("Invalid required four-wing assembly")
    if {w.id for w in wings}!={1,2,3,4} or {w.side for w in wings}!={-1,1}:
        raise ValueError("Unexpected wing side/id layout")
    if not all(40<s.length_cm<70 for s in supports):
        raise ValueError("Support span incompatible with approved review geometry")
    if not all(math.dist(c.location_cm,c.target_cm)>100 for c in CAMERAS):
        raise ValueError("Invalid review camera")
    return {
        "status":"SOURCE_GEOMETRY_PLAN_ONLY_NOT_NATIVE_BINDING",
        "review_map":MAP,
        "approved_reference_sha256":REFERENCE_SHA256,
        "wing_mesh":WING_PATH,
        "support_mesh":SUPPORT_PATH,
        "wings":[asdict(w) for w in wings],
        "supports":[asdict(s) for s in supports],
        "cameras":[asdict(c) for c in CAMERAS],
        "rig_animated":False,
        "native_build_accepted":False,
        "art_approved":False,
        "orbiter_authorized":False,
        "gameplay_modified":False,
    }

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--validate",action="store_true")
    args=parser.parse_args(argv)
    result=build_plan()
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":main()
