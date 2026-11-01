#!/usr/bin/env python3
"""Ender V2—reversible tailored-coat and swept-hair geometry study.

Derived from the validated Ender V1 generator. Not a rig, likeness approval,
hair-color decision, gameplay asset, or a modification of approved source art.
No asset installation or external modeling dependency.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

from build_cast import PALETTES, make
from build_ender_fidelity_v1 import (
    replace_part, face_head, add_face, add_hair, add_goggles, add_garment,
    split_bad_smooth_normal_faces,
)

VERSION = "ender_fidelity_v2"
COLOR_HOLD = "temporary V1 green; canonical Ender hair-color conflict NOT RESOLVED"
ORDER = "Reson > Aepex > Ender > Ionia > Lyra"

def make_card(builder, name, centers, widths, color, sideways="x"):
    """Smooth double-sided tapered hair ribbon along an organic centerline."""
    if len(centers) != len(widths) or len(centers) < 4:
        raise ValueError("Invalid tapered ribbon")
    vertices = []
    for (x, y, z), width in zip(centers, widths):
        if width <= 0:
            raise ValueError("Ribbon width must be positive")
        if sideways == "x":
            vertices.extend(((x-width/2, y, z), (x+width/2, y, z)))
        elif sideways == "z":
            vertices.extend(((x, y, z-width/2), (x, y, z+width/2)))
        else:
            raise ValueError("Unknown ribbon basis")
    faces = []
    for row in range(len(centers)-1):
        a=2*row
        faces.extend(((a,a+1,a+2),(a+1,a+3,a+2)))
    builder.mesh(name,vertices,faces,color,rough=0.88)

def replace_hair(builder):
    hair=PALETTES["Ender"]["hair"]
    builder.parts=[p for p in builder.parts
                   if not p[0].startswith("Hair strand ")
                   and p[0] != "Sculpt hair underlayer"]
    # Base cap is subtle. Layered paper-thin clumps overlap but leave eyes open.
    builder.ellipsoid("V2 tapered scalp underlayer",(0,1.623,-.022),
                      (.118,.080,.107),hair,segments=30,rings=18)
    shades=("#354c35","#435b45","#293f32","#50634a")
    # Comb-over/fringe cards: 23 differentiated tapered locks, not round rods.
    for i in range(23):
        t=i/22.
        x=-.105+.210*t
        s=math.sin(1.7*i)
        pts=[
            (x, 1.680+.004*s, -.030),
            (x-.010, 1.675+.003*s, .017),
            (x-.013+.006*s, 1.653+.003*s, .065),
            (x+.012*s, 1.616+.002*s, .100),
            (x+.018*s, 1.573+.009*math.sin(i*.8), .105),
        ]
        widths=(.012,.017,.018,.014,.0025)
        make_card(builder,"V2 fringe hair card %02d"%i,pts,widths,shades[i%4])
    # Side locks wrap temples and expose the ears instead of doming over them.
    for sign,label in ((-1,"L"),(1,"R")):
        for i in range(7):
            z=-.075+.025*i
            x=sign*(.106+.004*math.sin(i))
            pts=[
                (x, 1.660, z-.014),
                (x+sign*.005,1.624,z),
                (x+sign*.002,1.580,z+.008),
                (x-sign*.006,1.534+.005*(i%3),z+.015),
            ]
            make_card(builder,"V2 %s side hair card %02d"%(label,i),
                      pts,(.012,.016,.011,.0025),shades[(i+1)%4],sideways="z")
    for i in range(17):
        x=-.106+.212*i/16
        pts=[(x,1.668,-.089),(x+.003,1.636,-.111),
             (x+.005,1.577,-.114),(x*.90,1.532+.008*(i%3),-.099)]
        make_card(builder,"V2 nape hair card %02d"%i,pts,
                  (.013,.017,.013,.002),shades[i%4])
    # Subtle break in flat temple silhouette, not a new color decision.
    builder.ellipsoid("V2 crown crest",(0,1.677,-.025),
                      (.103,.022,.075),hair,segments=24,rings=10)

def tailor_coat(builder):
    # Remove four giant green oval front-panels, retaining shirt/waistcoat back.
    discarded={"L waistcoat front","R waistcoat front",
               "L waistcoat seam","R waistcoat seam"}
    existing={p[0] for p in builder.parts}
    if not discarded <= existing:
        raise ValueError("Missing V1 coat panels")
    builder.parts=[p for p in builder.parts if p[0] not in discarded]
    olive="#667044"
    edge="#bb8951"
    light="#8b9770"
    # Grid based connected fabric panel, with natural waist suppression and
    # gently curved chest. Replaces disconnected ellipsoids with sewn surfaces.
    for sign,label in ((-1,"L"),(1,"R")):
        verts=[];faces=[]
        rows=13;columns=8
        for r in range(rows):
            t=r/(rows-1)
            y=1.359-.464*t
            xinner=.016+.008*math.sin(t*math.pi)
            xouter=.163-.018*t+.006*math.sin(2.2*t)
            for c in range(columns):
                u=c/(columns-1)
                radius=xinner+(xouter-xinner)*u
                x=sign*radius
                z=.104+.031*math.sin(math.pi*u) - .008*t
                z+=.0035*math.sin(2*math.pi*t+1.2*u)*math.sin(math.pi*u)
                verts.append((x,y,z))
        for r in range(rows-1):
            for c in range(columns-1):
                a=r*columns+c;b=a+1;d=a+columns;f=d+1
                faces.extend(((a,b,d),(b,f,d)))
        builder.mesh("V2 "+label+" tailored waistcoat cloth",verts,faces,olive)
        # Integrated collar/lapel as a connected folded surface.
        lapel=[
          (sign*.020,1.356,.114),
          (sign*.075,1.342,.128),
          (sign*.106,1.301,.139),
          (sign*.073,1.240,.141),
          (sign*.057,1.277,.132),
        ]
        # Folded broken-line panel leaves the cream shirt visible.
        builder.mesh("V2 "+label+" shaped lapel",lapel,
                     [(0,1,4),(1,2,4),(2,3,4)],light)
        # Small stitch lines, not 3D tubing covering a large area.
        pts=[(sign*.051,1.339,.140),(sign*.076,1.315,.147),
             (sign*.079,1.278,.150),(sign*.064,1.245,.150)]
        builder.tube("V2 "+label+" lapel piping",pts,
                     [.0025,.003,.003,.002],edge,sides=7,metal=.35)
        for k in range(3):
            y=1.245-.094*k
            x=sign*(.151-.008*k)
            builder.tube("V2 "+label+" fabric shaping seam %d"%k,
                         [(x,y+.035,.110),(x-sign*.008,y,.119),
                          (x-sign*.013,y-.040,.114)],
                         [.0017,.0025,.0017],light,sides=7)
    # Cord tabs and lacing across the visible shirt opening.
    for i in range(4):
        y=1.27-.076*i
        builder.tube("V2 chest tab %d"%i,
                     [(-.026,y,.137),(-.005,y+.010,.142),(.026,y,.137)],
                     [.0035,.003,.0035],edge,sides=8,metal=.4)

def tune_eyes(builder):
    """Reduce oversized white/eye glints while keeping green irises obvious."""
    for side in ("L","R"):
        for label,sx,sy,sz in (
            (side+" sclera",.82,.84,1.0),
            (side+" iris",.92,.93,1.0),
            (side+" pupil",.95,.95,1.0),
        ):
            for idx,(name,verts,norms,faces,mat) in enumerate(builder.parts):
                if name != label:
                    continue
                mid=[sum(v[k] for v in verts)/len(verts) for k in range(3)]
                new=[tuple(mid[k]+(v[k]-mid[k])*((sx,sy,sz)[k])
                           for k in range(3)) for v in verts]
                # Rebuild part normals (smooth) through Builder.mesh.
                old=builder.parts.pop(idx)
                color=builder.materials[mat]["name"]
                builder.mesh(label,new,faces,color)
                break
            else:
                raise ValueError("Missing eye material region "+label)

def quantize_geometry(builder):
    """Round authored mesh values prior to binary glTF serialization.

    This narrows host-dependent trigonometric float noise. Cross-platform
    SHA parity must still be proved in real CI; never assume it.
    """
    new=[]
    for name,vs,ns,faces,mat in builder.parts:
        verts=[tuple(round(float(x),5) for x in p) for p in vs]
        norms=[tuple(round(float(x),6) for x in n) for n in ns]
        if any(not math.isfinite(x) for p in verts+norms for x in p):
            raise ValueError("Nonfinite mesh coordinate")
        new.append((name,verts,norms,faces,mat))
    builder.parts=new

def build(out):
    out=Path(out)
    if (out/("Ender_"+VERSION+".glb")).exists() or (out/"receipt.json").exists():
        raise FileExistsError("Immutable review candidate: no overwrite")
    builder=make("Ender")
    for part in ("Head sculpt","Hair crown","Nose","Mouth",
                 "L brow","R brow","Goggle rim -1","Goggle rim 1"):
        replace_part(builder,part,lambda _:None)
    face_head(builder)
    add_face(builder)
    add_hair(builder)
    add_goggles(builder)
    add_garment(builder)
    tailor_coat(builder)
    replace_hair(builder)
    tune_eyes(builder)
    normal_fixes=split_bad_smooth_normal_faces(builder)
    quantize_geometry(builder)
    if len({p[0] for p in builder.parts})!=len(builder.parts):
        raise ValueError("Duplicate part names")
    out.mkdir(parents=True,exist_ok=True)
    source=builder.save(out/("Ender_"+VERSION+".glb"))
    receipt={
      "status":"NONCANONICAL_UNRIGGED_TAILORING_HAIR_V2_STUDY",
      "name":"Ender","version":VERSION,
      "source":source,
      "normal_fix_counts":normal_fixes,
      "height_order_canon":ORDER,
      "hair_color_state":COLOR_HOLD,
      "inherits":"V1 original Ender procedural study",
      "original_approved_art_replaced":False,
      "baseline_glb_changed":False,
      "source_baseline_untouched":True,
      "art_approval":False,"gameplay_ready":False
    }
    (out/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    print(json.dumps(build(args.output),indent=2))
