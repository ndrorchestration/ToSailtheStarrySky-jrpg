#!/usr/bin/env python3
"""Deterministic, REVIEW-ONLY Aureate Wake cinematic-detail GLB accessory pack.

Five independently importable pieces for one unchanged shared vessel:
shared exterior trim, Skybourne wing filigree, Seabourne foil fittings,
Submersible light rail, and a single Starbourne radial sail motif.
No gameplay actor, form request, physics, pressure rating or story gate.
All coordinates are design-study centimetres (+X forward, +Z up).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path

from build_aureate_body_review import Surface, encode_glb, STATUS

APPROVED_ART_SHA = "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13"
PROVENANCE = "NONCANONICAL_CINEMATIC_V4_DETAIL_ACCESSORIES"
FORM_NAMES = ("Skybourne", "Seabourne", "Submersible", "Starbourne")
CORE = "AureateWake_SharedExteriorTrim_V4_REVIEW.glb"
SKY = "AureateWake_SkybourneWingFiligree_V4_REVIEW.glb"
SEA = "AureateWake_SeabourneHydrofoilDetail_V4_REVIEW.glb"
SUB = "AureateWake_SubmersibleLightRail_V4_REVIEW.glb"
STAR = "AureateWake_StarbourneSailMotif_V4_REVIEW.glb"
FILES = (CORE, SKY, SEA, SUB, STAR)
MANIFEST = "AureateWake_CinematicDetailV4_Manifest.json"
REVIEW_ROOT = "/Game/TSTSS/Review/ShipArt/CinematicV4"


class StableUVSurface(Surface):
    """Per-triangle dominant-axis UVs; avoids collapsed tangent bases on side faces."""
    def tri(self, a, b, c):
        previous = len(self.pos)
        super().tri(a, b, c)
        if len(self.pos) == previous:
            return
        ab = [b[i] - a[i] for i in range(3)]
        ac = [c[i] - a[i] for i in range(3)]
        cross = (ab[1]*ac[2] - ab[2]*ac[1],
                 ab[2]*ac[0] - ab[0]*ac[2],
                 ab[0]*ac[1] - ab[1]*ac[0])
        main = max(range(3), key=lambda i: abs(cross[i]))
        axes = ((1,2), (0,2), (0,1))[main]
        self.uv[-3:] = [tuple(p[i] / 100.0 for i in axes) for p in (a,b,c)]


def surfaces():
    return [StableUVSurface(name) for name in
            ("PearlIvoryInlays", "WarmBrassFiligree",
             "MidnightNavyMechanics", "CyanResonanceAccents")]


def arc(surface, points, radius=1.2, sides=8):
    for a,b in zip(points,points[1:]):
        surface.tube(a,b,radius,sides,False)


def circle(surface, center, radii, axis, segments=24, radius=1.0):
    pts = []
    for i in range(segments+1):
        a = 2*math.pi*i/segments
        if axis == "x":
            pts.append((center[0],center[1]+radii[0]*math.cos(a),
                        center[2]+radii[1]*math.sin(a)))
        elif axis == "z":
            pts.append((center[0]+radii[0]*math.cos(a),
                        center[1]+radii[1]*math.sin(a),center[2]))
        else:
            raise ValueError("unsupported review ring axis")
    arc(surface,pts,radius)


def shared_exterior():
    pearl,gold,navy,cyan = surfaces()
    # Repeated centerline features belong to one hull; NOT a new form-specific hull.
    stations = [(-370,30),(-310,53),(-205,66),(-50,73),
                (155,72),(260,60),(345,29),(390,9)]
    for side in (-1,1):
        for (x0,w0),(x1,w1) in zip(stations,stations[1:]):
            gold.tube((x0,side*w0*.90,17),(x1,side*w1*.90,17),1.2,8,False)
            pearl.tube((x0,side*w0*.77,27),(x1,side*w1*.77,27),1.8,8,False)
        # Brass-framed, blue-accented observation ports, not pressure-rated windows.
        for x in (-255,-180,-105,35,120):
            w = 63 if x < -50 else 69
            circle(gold,(x,side*w,8),(10.5,8.2),"x",18,1.4)
            navy.block(x-5,x+5,min(side*w-1,side*w+1),max(side*w-1,side*w+1),4,12)
            cyan.tube((x-3,side*(w+2),8),(x+3,side*(w+2),8),1.2,6)
        # Observation deck low-profile recessed glowing trim.
        cyan.tube((205,side*29,33),(340,side*14,23),0.8,6,False)
    # Two separate nacelle collar circles; no propulsion mechanics claim.
    for x in (-326,-293,-266):
        circle(gold,(x,0,1),(43,29),"x",32,1.8)
    navy.block(-330,-252,-22,22,23,31)
    cyan.block(-310,-286,-9,9,32,34)
    # Central living quarters remain in the same shared hull.
    pearl.block(-78,70,-25,25,35,39)
    for x in (-60,-25,10,45):
        gold.tube((x,-25,40),(x,25,40),.85,6)
    return [pearl,gold,navy,cyan]


def skybourne_wing_lace():
    pearl,gold,navy,cyan = surfaces()
    # Root-pivoted +X wing accessory inside the existing 280cm span.
    widths = ((12,13),(40,26),(95,37),(150,39),(208,27),(259,7))
    for side in (-1,1):
        pts=[(x,side*w,3) for x,w in widths]
        arc(gold,pts,1.6)
        for x,w in widths[1:-1]:
            gold.tube((8,0,5),(x,side*w,3),.72,7,False)
            cyan.tube((x,side*w*.45,4),(x+12,side*w*.5,4),.6,6,False)
    navy.block(0,26,-13,13,-6,7)
    pearl.tube((0,0,8),(257,0,8),2.0,8,False)
    circle(gold,(13,0,4),(15,9),"x",16,.8)
    cyan.block(230,257,-2.0,2.0,8,10)
    return [pearl,gold,navy,cyan]


def seabourne_hydrofoil():
    pearl,gold,navy,cyan = surfaces()
    # Local accessory per existing foil; two instances, not two additional foils.
    pearl.block(-101,101,-35,35,-5,3)
    navy.block(-77,77,-14,14,3,9)
    for side in (-1,1):
        gold.tube((-98,side*32,5),(96,side*32,5),1.7,8,False)
        gold.tube((-70,side*12,10),(70,side*12,10),1.2,8,False)
        cyan.tube((-64,side*21,9),(64,side*21,9),.8,8,False)
    # Capped joint rings and two visible trim fins for ocean silhouette.
    for x in (-65,65):
        circle(gold,(x,0,11),(23,10),"z",20,1.0)
    cyan.block(90,98,-12,12,6,8)
    return [pearl,gold,navy,cyan]


def submersible_light_rail():
    pearl,gold,navy,cyan = surfaces()
    # Entire ship-root accessory: visual cues for a pressure-ready LOOK only.
    for side in (-1,1):
        y = side*65
        navy.block(-245,205,min(y-4,y+4),max(y-4,y+4),-13,-1)
        pearl.tube((-245,y,-2),(205,y,-2),2.0,8,False)
        gold.tube((-236,side*71,-10),(193,side*71,-10),1.1,8,False)
        for x in (-215,-135,-55,25,105,183):
            circle(gold,(x,side*69,-6),(8,8),"x",16,.8)
            cyan.block(x-4,x+4,min(side*70,side*73),
                       max(side*70,side*73),-10,-4)
    # Two stern light fins remain part of the same hull ornament.
    for side in (-1,1):
        gold.tube((-330,side*19,-12),(-285,side*45,-26),2.1,8,False)
        cyan.tube((-333,side*19,-12),(-303,side*35,-21),1.0,6,False)
    return [pearl,gold,navy,cyan]


def starbourne_sail_motif():
    pearl,gold,navy,cyan = surfaces()
    # ONE identical reusable sail decoration, instanced four times in a STATIC
    # developer study. This is NOT a fifth wing or a runtime Orbiter transform.
    sections = [(16,13),(45,38),(103,68),(157,74),(214,43),(268,10)]
    for (x0,w0),(x1,w1) in zip(sections,sections[1:]):
        cyan.quad((x0,-w0,2),(x1,-w1,2),(x1,w1,2),(x0,w0,2))
    for side in (-1,1):
        arc(gold,[(x,side*w,6) for x,w in sections],1.75)
        for x,w in sections[1:-1]:
            gold.tube((12,0,9),(x,side*w,6),.95,8,False)
            pearl.tube((x,0,8),(x,side*w*.65,7),.75,8,False)
    navy.block(0,33,-17,17,-7,8)
    pearl.tube((0,0,10),(270,0,10),2.25,8,False)
    cyan.block(235,258,-2.2,2.2,11,13)
    return [pearl,gold,navy,cyan]


def mat(name,color,metal,rough,emissive=None,alpha=None):
    result = {"name": name+"_NONCANONICAL_REVIEW",
              "pbrMetallicRoughness":{
                  "baseColorFactor":color,"metallicFactor":metal,
                  "roughnessFactor":rough},"doubleSided":True}
    if emissive: result["emissiveFactor"]=emissive
    if alpha: result["alphaMode"]="BLEND"
    return result


MATERIALS = [
    mat("PearlescentEnamel",[.95,.87,.71,1],.26,.27),
    mat("WarmFiligreeGold",[.81,.49,.16,1],.87,.22),
    mat("MidnightNavyStructure",[.025,.075,.15,1],.63,.35),
    mat("CyanResonanceLight",[.08,.49,.85,.72],.27,.24,[.07,.26,.52],"BLEND"),
]
BUILDERS = ((CORE,shared_exterior),(SKY,skybourne_wing_lace),
            (SEA,seabourne_hydrofoil),(SUB,submersible_light_rail),
            (STAR,starbourne_sail_motif))
ATTACHMENTS = {
    CORE: {"kind":"ship_root","instances":1,"states":list(FORM_NAMES)},
    SKY: {"kind":"existing_wing_root","instances":4,"states":["Skybourne"]},
    SEA: {"kind":"existing_hydrofoil","instances":2,"states":["Seabourne"]},
    SUB: {"kind":"ship_root","instances":1,"states":["Submersible"]},
    STAR: {"kind":"static_developer_study_only","instances":4,
           "states":["Starbourne"],"requires_story_unlock":True},
}


def payloads():
    return {name:encode_glb(name[:-4],builder(),MATERIALS)
            for name,builder in BUILDERS}


def receipt(blobs):
    return {"stage":PROVENANCE,"status":STATUS,
            "original_approved_image_sha256":APPROVED_ART_SHA,
            "canonical_form_names":list(FORM_NAMES),
            "candidate_import_folder":REVIEW_ROOT,
            "attachment_plan_review_only":ATTACHMENTS,
            "sha256":{k:hashlib.sha256(v).hexdigest() for k,v in blobs.items()},
            "source_units":"UE_cm_Xforward_Zup",
            "gltf_units":"meters_Yup",
            "material_sections_each":len(MATERIALS),
            "native_unreal_import":"NOT_VERIFIED",
            "native_unreal_render":"NOT_VERIFIED",
            "swept_collision":"NOT_VERIFIED",
            "creator_model_approved":False,
            "starbourne_gameplay_unlocked":False,
            "form_enum_or_save_schema_changed":False,
            "production_content_changed":False}


def build_or_verify(path:Path, build:bool):
    path = path.resolve()
    if build: path.mkdir(parents=True,exist_ok=True)
    if not path.is_dir(): raise ValueError("Review output folder missing")
    blobs = payloads()
    report = receipt(blobs)
    expected = {**blobs, MANIFEST:(json.dumps(report,indent=2,sort_keys=True)+"\n").encode()}
    unexpected = {f.name for f in path.iterdir()}-set(expected)
    if unexpected: raise ValueError("Refusing occupied folder: "+repr(unexpected))
    for name,data in expected.items():
        dest=path/name
        if dest.exists():
            if dest.is_symlink() or not dest.is_file() or dest.read_bytes()!=data:
                raise ValueError("Refusing to overwrite different asset: "+name)
        elif build:dest.write_bytes(data)
        else:raise ValueError("Missing candidate: "+name)
    return report


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir",required=True,type=Path)
    task=parser.add_mutually_exclusive_group(required=True)
    task.add_argument("--build",action="store_true")
    task.add_argument("--verify",action="store_true")
    args=parser.parse_args(argv)
    print(json.dumps(build_or_verify(args.output_dir,args.build),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
