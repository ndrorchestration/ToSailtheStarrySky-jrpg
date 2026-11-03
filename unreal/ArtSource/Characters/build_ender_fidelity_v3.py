#!/usr/bin/env python3
"""Ender V3: a measured, *noncanonical* head-and-hair landmark geometry study.

This stage is still procedural static lookdev, NOT a cinematic sculpt/rig/approval.
It adds a reversible derived GLB beside immutable original, V1 and V2 files.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from build_cast import make, PALETTES
from build_ender_fidelity_v1 import (
    replace_part, face_head, add_face, add_hair, add_goggles, add_garment,
    split_bad_smooth_normal_faces,
)
from build_ender_fidelity_v2 import tailor_coat, replace_hair, tune_eyes, quantize_geometry, make_card

VERSION = "ender_head_landmark_v3"
ORDER = "Reson > Aepex > Ender > Ionia > Lyra"
COLOR_HOLD = "TEMPORARY GREEN; reference copper/auburn versus green NOT RESOLVED"
BASELINES = {
    "Candidates/Ender.glb": "d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2",
    "FidelityCandidates/EnderV1/Ender_ender_face_hair_v1.glb":
        "3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38",
    "FidelityCandidates/EnderV2/Ender_ender_fidelity_v2.glb":
        "e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8",
}
# Sculpt reference-space coordinates are provisional engineering study values in
# source metres, not measurements inferred from 2D imagery or canon dimensions.
LANDMARKS = {
    "left_eye_center": (-.047, 1.514, .117),
    "right_eye_center": (.047, 1.514, .117),
    "nose_tip": (0, 1.479, .138),
    "mouth_center": (0, 1.443, .118),
    "chin_center": (0, 1.376, .068),
    "left_cheek_anchor": (-.077, 1.478, .070),
    "right_cheek_anchor": (.077, 1.478, .070),
}
ROOT = Path(__file__).resolve().parent


def baseline_receipts():
    actual = {}
    for relative, expected in BASELINES.items():
        p = ROOT / relative
        if not p.is_file():
            raise FileNotFoundError("Pinned predecessor missing: " + relative)
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        if sha != expected:
            raise ValueError("Pinned original/V1/V2 changed: " + relative)
        actual[relative] = sha
    return actual


def shape_face(builder):
    """Deform only V2 face surface with soft eye-socket/cheek/chin planes.

    Keeps eyes, nose, ear and goggles separate for future actual retopology.
    """
    name = "Sculpt face with jaw"
    face = [p for p in builder.parts if p[0] == name]
    if len(face) != 1:
        raise ValueError("V2 face base missing or ambiguous")
    _, vs, _, faces, mat = face[0]
    builder.parts = [p for p in builder.parts if p[0] != name]
    new = []
    for x,y,z in vs:
        fx=abs(x)
        xx=x
        zz=z
        if z > 0:
            # Orbital socket recession under the brow; smooth Gaussian support.
            socket = math.exp(-((fx-.046)/.032)**2 - ((y-1.518)/.027)**2)
            zz -= .0060 * socket
            # Subtle cheek volume immediately below the outer orbital area.
            malar = math.exp(-((fx-.071)/.043)**2 - ((y-1.474)/.032)**2)
            zz += .0070 * malar
            xx *= 1 + .028 * malar
            # Reduce toy-like roundness along the lower cheeks.
            if y < 1.454:
                t=max(0.0,min(1.0,(1.454-y)/.085))
                xx *= 1 - .042*t
                zz += .0035*t
            # Brow saddle and soft chin tip without a separate button mesh.
            brow = math.exp(-((fx-.05)/.052)**2 - ((y-1.557)/.021)**2)
            zz += .0025*brow
            chin = math.exp(-(fx/.044)**2 - ((y-1.393)/.025)**2)
            zz += .003*chin
        new.append((xx,y,zz))
    builder.mesh("V3 face sculpt orbital cheek chin planes", new, faces,
                 PALETTES["Ender"]["skin"], rough=.87)
    # A restrained lower orbital edge, not a thick cartoon white border.
    for label, sign in (("L",-1),("R",1)):
        x=sign*.048
        pts=[(x-.027,1.502,.103),(x-.013,1.496,.114),
             (x,1.495,.119),(x+.014,1.497,.114),(x+.026,1.503,.103)]
        builder.tube("V3 "+label+" lower orbital fold",pts,
                     [.0013,.0015,.0015,.0015,.0013],
                     "#bc8b76",sides=8,rough=.94)


def sweep_hair(builder):
    """Replace V2 flat symmetric fringe with controlled asymmetrical flowing locks.

    The green study color remains explicitly temporary. No simulation, texture
    groom, scalp UVs, strand physics or artistic hair-color decision is implied.
    """
    previous=[p[0] for p in builder.parts
              if p[0].startswith(("V2 fringe hair card ","V2 L side hair card ",
                                  "V2 R side hair card ","V2 nape hair card "))]
    if len(previous) != 54:
        raise ValueError("V2 hair-card set changed unexpectedly: "+str(len(previous)))
    builder.parts=[p for p in builder.parts if p[0] not in previous]
    hues=("#324736","#42563b","#354b39","#536448")
    # 28 interleaved front locks.  Each has a smoothly biased direction,
    # softly curved z, and taper to a nonuniform hairline.
    for i in range(28):
        t=i/27
        x=-.113+.226*t
        sway=.010*math.sin(.58*i+1.1)
        drift=.014*math.sin(2.3*t+0.6)+.007*(t-.5)
        tip_y=1.579+.021*math.sin(i*1.41)+.009*t
        pts=[
            (x,1.678+.006*math.sin(.9*i),-.033),
            (x+.30*drift,1.667+.003*math.sin(i),.002),
            (x+.65*drift,1.646+.004*math.sin(i*.7),.047),
            (x+drift+sway*.25,1.624,.080),
            (x+1.3*drift+sway,1.604,.100),
            (x+1.5*drift+sway,tip_y,.100),
        ]
        make_card(builder,"V3 swept front lock %02d"%i,pts,
                  (.012,.016,.019,.016,.010,.0018),hues[i%4])
    # Side/nape remain attached around the cranium rather than projecting flat.
    for sign,label in ((-1,"L"),(1,"R")):
        for i in range(8):
            z=-.080+.025*i
            x=sign*(.106+.003*math.sin(i))
            pts=[(x,1.670,z-.025),(x+sign*.008,1.644,z-.009),
                 (x+sign*.010,1.604,z+.006),
                 (x+sign*.002,1.568,z+.016),
                 (x-sign*.005,1.532+.008*(i%3),z+.018)]
            make_card(builder,"V3 "+label+" temple lock %02d"%i,pts,
                      (.011,.015,.015,.010,.002),hues[(i+2)%4],sideways="z")
    for i in range(18):
        x=-.110+.220*i/17
        pts=[(x,1.668,-.086),(x+.004,1.648,-.112),
             (x+.003,1.610,-.126),(x*.94,1.557,-.122),
             (x*.85,1.523+.008*(i%4),-.112)]
        make_card(builder,"V3 nape sweep %02d"%i,pts,
                  (.011,.017,.017,.010,.002),hues[(i+1)%4])


def build(out):
    out=Path(out)
    glb=out/("Ender_"+VERSION+".glb")
    if glb.exists() or (out/"receipt.json").exists():
        raise FileExistsError("Immutable Ender V3: refuse overwriting any prior evidence")
    baselines=baseline_receipts()
    b=make("Ender")
    for name in ("Head sculpt","Hair crown","Nose","Mouth",
                 "L brow","R brow","Goggle rim -1","Goggle rim 1"):
        replace_part(b,name,lambda _:None)
    face_head(b)
    add_face(b)
    add_hair(b)
    add_goggles(b)
    add_garment(b)
    tailor_coat(b)
    replace_hair(b)
    tune_eyes(b)
    shape_face(b)
    sweep_hair(b)
    fixes=split_bad_smooth_normal_faces(b)
    quantize_geometry(b)
    names=[p[0] for p in b.parts]
    if len(set(names))!=len(names):
        raise ValueError("Repeated named geometry parts")
    out.mkdir(parents=True,exist_ok=True)
    source=b.save(glb)
    receipt={
      "status":"NONCANONICAL_UNRIGGED_HEAD_LANDMARK_V3_STUDY",
      "name":"Ender","version":VERSION,"source":source,
      "pinned_predecessors":baselines,
      "normal_fix_counts":fixes,
      "head_landmarks_source_m":LANDMARKS,
      "reference_space_measured_from_approved_image":False,
      "hair_color_state":COLOR_HOLD,
      "height_order_canon":ORDER,
      "source_baseline_untouched":True,
      "full_body_v2_remaining_design_preserved":True,
      "approved_art_replaced":False,"production_pawn_changed":False,
      "skin_or_rigged":False,"creator_approval":False,
      "art_approval":False,"gameplay_ready":False,
      "next_gate":"native import and matched head-turnaround visual comparison"
    }
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(build(args.output),indent=2))
