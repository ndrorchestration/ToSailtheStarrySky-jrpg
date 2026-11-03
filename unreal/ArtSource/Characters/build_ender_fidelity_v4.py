#!/usr/bin/env python3
"""Ender V4: separate facial-plane topology/feature-proportion STUDY, not approved likeness.

Original/EnderV1/V2/V3 meshes and author-approved reference assets untouched.
Source coordinates are engineering hypotheses, NOT image-measured landmarks.
This is *not* a retopologized animation-quality head or a skinned asset.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from build_cast import make, PALETTES
from build_ender_fidelity_v1 import (
    replace_part,face_head,add_face,add_hair,add_goggles,add_garment,
    split_bad_smooth_normal_faces,
)
from build_ender_fidelity_v2 import tailor_coat,replace_hair,tune_eyes,quantize_geometry
from build_ender_fidelity_v3 import shape_face,sweep_hair,BASELINES as PREDECESSORS,ORDER,COLOR_HOLD

VERSION="ender_anatomy_v4"
ROOT=Path(__file__).resolve().parent
V3_REL="FidelityCandidates/EnderV3/Ender_ender_head_landmark_v3.glb"
V3_SHA="0fb1b6e8de8d84ce751ce8bbb97b7ca78174e077acf64f60e127bd0ddb90c2de"
PREDECESSOR_HASHES={**PREDECESSORS,V3_REL:V3_SHA}
# Deliberately model-space provisional points; no inference that a generated image
# supplies precise anthropometric ground truth.
LANDMARKS={
    "left_orbit":(-.046,1.519,.095),"right_orbit":(.046,1.519,.095),
    "nose_bridge":(0,1.526,.113),"nose_tip":(0,1.480,.127),
    "mouth_midline":(0,1.442,.117),"chin":(0,1.388,.087),
    "left_ear_anchor":(-.117,1.502,.014),
    "right_ear_anchor":(.117,1.502,.014)
}

def check_predecessors():
    checked={}
    for rel,expected in PREDECESSOR_HASHES.items():
        p=ROOT/rel
        if not p.is_file():raise FileNotFoundError(rel)
        actual=hashlib.sha256(p.read_bytes()).hexdigest()
        if actual!=expected:raise ValueError("Predecessor source drift: "+rel)
        checked[rel]=actual
    return checked

def assemble_v3():
    """Generate source-equivalent V3 components in memory; never write old GLB."""
    b=make("Ender")
    for name in ("Head sculpt","Hair crown","Nose","Mouth",
                 "L brow","R brow","Goggle rim -1","Goggle rim 1"):
        replace_part(b,name,lambda _:None)
    face_head(b);add_face(b);add_hair(b);add_goggles(b);add_garment(b)
    tailor_coat(b);replace_hair(b);tune_eyes(b)
    shape_face(b);sweep_hair(b)
    return b

def retopology_study_face(builder):
    """An original closed ring-based face surface with parameterized jaw/cheek/brow
    sections; genuine oriented quad-strip topology, *not* animation retopology.
    """
    old="V3 face sculpt orbital cheek chin planes"
    replace_part(builder,old,lambda _:None)
    skin=PALETTES["Ender"]["skin"]
    seg=48
    rings=32
    cy=1.505;ry=.143
    verts=[(0,cy+ry,.006)]
    for j in range(1,rings):
        phi=math.pi*j/rings
        yy=cy+ry*math.cos(phi)
        rr=math.sin(phi)
        # Jaw V4: reduced lower cheek mass, slightly stronger malar planes.
        jaw_t=max(0., min(1.,(1.490-yy)/.105))
        xr=.111*rr*(1-.19*jaw_t)
        zr=.105*rr*(1-.025*jaw_t)
        for i in range(seg):
            theta=2*math.pi*i/seg
            x=xr*math.cos(theta)
            z=.005+zr*math.sin(theta)
            if z>0.005:
                absx=abs(x)
                # Local recessed orbital areas, cheekbone rise, smooth nose bridge.
                eye=math.exp(-((absx-.046)/.030)**2-((yy-1.519)/.024)**2)
                malar=math.exp(-((absx-.070)/.042)**2-((yy-1.474)/.035)**2)
                brow=math.exp(-((absx-.045)/.05)**2-((yy-1.555)/.018)**2)
                bridge=math.exp(-(x/.018)**2-((yy-1.514)/.041)**2)
                tip=math.exp(-(x/.015)**2-((yy-1.478)/.012)**2)
                chin=math.exp(-(x/.045)**2-((yy-1.392)/.022)**2)
                z+=-.0057*eye+.0040*malar+.0020*brow+.010*bridge+.009*tip+.003*chin
            verts.append((x,yy,z))
    south=len(verts);verts.append((0,cy-ry,.006))
    faces=[]
    for i in range(seg):
        a=1+i;b=1+(i+1)%seg
        faces.append((0,b,a))
    for j in range(rings-2):
        for i in range(seg):
            a=1+j*seg+i
            b=1+j*seg+(i+1)%seg
            d=a+seg
            c=b+seg
            faces.extend(((a,b,d),(b,c,d)))
    for i in range(seg):
        a=1+(rings-2)*seg+i
        b=1+(rings-2)*seg+(i+1)%seg
        faces.append((a,b,south))
    builder.mesh("V4 closed facial topology cheek jaw and orbital volumes",verts,faces,skin,rough=.87)

def replace_facial_features(builder):
    """Reduce detached/oversized features with smaller bone-anchored primitives.
    Eyes, ears and nose remain separately addressable for future true sculpt/rig.
    """
    discarded={"Left ear","Right ear",
               "Sculpt nasal bridge","Sculpt nose tip",
               "Sculpt nasal ala L","Sculpt nasal ala R",
               "Nostril L","Nostril R",
               "Sculpt ear helix L","Sculpt ear helix R",
               "Eyelid L upper","Eyelid R upper","Eyelid L lower","Eyelid R lower",
               "V3 L lower orbital fold","V3 R lower orbital fold"}
    for side in ("L","R"):
        discarded.update({side+" sclera",side+" iris",side+" pupil",side+" eye glint"})
    oldnames={p[0] for p in builder.parts}
    if not discarded<=oldnames:
        raise ValueError("Unexpected V3 feature source: "+str(sorted(discarded-oldnames)))
    builder.parts=[p for p in builder.parts if p[0] not in discarded]
    skin=PALETTES["Ender"]["skin"]
    for side,sgn in (("L",-1),("R",1)):
        # Ears fall within lower half of orbit/upper nose, instead of long slabs.
        builder.ellipsoid("V4 "+side+" anatomically scaled ear",
                          (sgn*.115,1.501,.009),(.0145,.029,.0195),
                          skin,segments=22,rings=14,rough=.89)
        builder.tube("V4 "+side+" antihelix contour",
                     [(sgn*.127,1.513,.021),(sgn*.130,1.502,.029),
                      (sgn*.126,1.484,.023)],
                     [.0019,.0021,.0015],"#b88169",sides=9,rough=.9)
        x=sgn*.046
        # The V3 sclera were prominent, detached ovals. Use a smaller shallow
        # almond-oriented eye; still only an unrigged topology proposal.
        builder.ellipsoid("V4 "+side+" shallow eye almond",
                          (x,1.515,.096),(.020,.0085,.004),
                          "#e6d7c1",segments=24,rings=12,rough=.43)
        builder.ellipsoid("V4 "+side+" green iris",
                          (x,1.515,.100),(.0068,.0072,.0022),
                          "#3aaa68",segments=20,rings=10,rough=.36)
        builder.ellipsoid("V4 "+side+" narrow pupil",
                          (x,1.515,.102),(.0027,.005,.0012),
                          "#211b18",segments=16,rings=10,rough=.28)
        upper=[(x-.022,1.518,.096),(x-.011,1.524,.101),
               (x,1.525,.103),(x+.011,1.524,.101),(x+.022,1.518,.096)]
        lower=[(x-.020,1.511,.094),(x,1.507,.101),(x+.020,1.511,.094)]
        builder.tube("V4 "+side+" upper lid edge",upper,
                     [.0014,.0017,.0017,.0017,.0014],skin,sides=8)
        builder.tube("V4 "+side+" lower lid edge",lower,
                     [.0011,.0012,.0011],"#b98c75",sides=8)
    # Smaller cartilage-defined bridge/nose tip; integrated nose volume already
    # comes from the V4 facial surface, these are restrained local overlays.
    builder.tube("V4 narrow nasal dorsum",
                 [(0,1.538,.111),(0,1.516,.119),(0,1.497,.124),
                  (0,1.481,.127)],
                 [.0060,.0072,.0080,.0060],skin,sides=16,rough=.85)
    builder.ellipsoid("V4 restrained nasal tip",(0,1.477,.130),
                      (.0125,.0080,.0080),skin,segments=24,rings=12)
    for side,sgn in (("L",-1),("R",1)):
        builder.ellipsoid("V4 "+side+" alar wing",
                          (sgn*.0115,1.474,.126),(.0070,.006,.0055),
                          skin,segments=16,rings=10)
        builder.ellipsoid("V4 "+side+" nostril shadow",
                          (sgn*.011,1.469,.130),(.0030,.0014,.0013),
                          "#775348",segments=12,rings=8)

def build(out):
    out=Path(out)
    target=out/("Ender_"+VERSION+".glb")
    if target.exists() or (out/"receipt.json").exists():
        raise FileExistsError("Immutable V4 source candidate: no overwrite")
    preds=check_predecessors()
    b=assemble_v3()
    retopology_study_face(b)
    replace_facial_features(b)
    normals=split_bad_smooth_normal_faces(b)
    quantize_geometry(b)
    if len({p[0] for p in b.parts})!=len(b.parts):
        raise ValueError("Duplicate face study part names")
    out.mkdir(parents=True,exist_ok=True)
    source=b.save(target)
    receipt={
      "status":"V4_UNRIGGED_NONCANONICAL_FACIAL_TOPOLOGY_STUDY",
      "source":source,"version":VERSION,"name":"Ender",
      "pinned_predecessors":preds,"source_baseline_untouched":True,
      "normal_fix_counts":normals,
      "model_space_landmarks_m":LANDMARKS,
      "reference_space_measured_from_approved_image":False,
      "approved_references":"2026-10-30 core cast and separate historical Ender solarpunk sheet; contrasting artistic styles",
      "unresolved_hair_color":"dark/green cast variant versus auburn/brown solarpunk sheet; HOLD",
      "height_order_canon":ORDER,
      "author_approved_likeness":False,"cinematic_quality":False,
      "approved_art_replaced":False,"v3_replaced":False,
      "skinned":False,"rigged":False,"animation_ready":False,
      "production_game_asset":False,
      "native_import_verified":False,
      "native_render_verified":False,
      "art_approval":False,
      "topology_intent":"closed mesh with radial longitudinal rings; not production animation retopology",
      "next_gate":"Unreal 5.8.4 isolated native import and close-up visual acceptance"
    }
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(build(args.output),indent=2))
