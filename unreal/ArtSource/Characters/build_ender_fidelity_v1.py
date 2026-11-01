#!/usr/bin/env python3
"""Ender facial/hair refinement STUDY — original procedural geometry, not approved art.

Builds an isolated new GLB; never replaces the five baseline Candidates/*.glb.
Only Ender is altered, using the existing Builder geometry and provenance gates.
Color is a temporary existing palette, NOT an art decision about Ender's hair.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from build_cast import make, PALETTES

VERSION = "ender_face_hair_v1"
NEW_PART_PREFIX = ("Sculpt ", "Hair strand ", "Eyelid ", "Nostril ", "Garment ")

def replace_part(builder, name, callback):
    old = [part for part in builder.parts if part[0] == name]
    if len(old) != 1:
        raise ValueError("Expected exactly one "+name)
    builder.parts = [part for part in builder.parts if part[0] != name]
    callback(builder)

def face_head(builder):
    name="Head sculpt"
    # Improve the basic ellipsoid by adjusting skull, jaw and chin relative to
    # head height; separate from eyes/ears/accessories, so later sculpt swaps are safe.
    builder.ellipsoid("Sculpt face with jaw", (0, 1.505, .004),
                      (.110, .143, .104), PALETTES["Ender"]["skin"],
                      segments=32, rings=22)
    idx=next(i for i,x in enumerate(builder.parts) if x[0]=="Sculpt face with jaw")
    pname,verts,_,faces,mat=builder.parts.pop(idx)
    edited=[]
    for x,y,z in verts:
        if y < 1.43:
            r=max(0.,min(1.,(y-1.36)/.07))
            x*=.70+.27*r
            z+=.004*(1-r)
        elif y < 1.50:
            r=(y-1.43)/.07
            x*=.97+.04*math.sin(r*math.pi)
            z+=.003*math.sin(r*math.pi)
        elif y > 1.59:
            x*=1-.06*min(1,(y-1.59)/.06)
        # Subtle flattened brow/forehead, keeping eyes on +Z.
        if y > 1.52 and z > 0:
            z-=.004*min(1,(y-1.52)/.05)
        edited.append((x,y,z))
    # Builder recomputes smooth vertex normals from the edited surface.
    builder.mesh(pname,edited,faces,PALETTES["Ender"]["skin"])

def curved(builder,name,pts,radius,color,metal=0,rough=.75,sides=10):
    builder.tube(name,pts,[radius for _ in pts],color,sides=sides,metal=metal,rough=rough)

def add_face(builder):
    skin=PALETTES["Ender"]["skin"]
    hair=PALETTES["Ender"]["hair"]
    # Eye contours instead of disconnected white ovals; retain green iris.
    for side,sign in (("L",-1),("R",1)):
        x=sign*.047
        upper=[(x-.028,1.520,.108),(x-.014,1.531,.115),
               (x,1.532,.120),(x+.014,1.531,.115),(x+.028,1.520,.108)]
        lower=[(x-.025,1.507,.112),(x,1.502,.120),(x+.025,1.507,.112)]
        curved(builder,"Eyelid "+side+" upper",upper,.0038,skin)
        curved(builder,"Eyelid "+side+" lower",lower,.0028,"#b98870")
        # Deliberate understated brow arcs; not giant straight cylinders.
        curved(builder,"Sculpt "+side+" eyebrow",
               [(x-.030,1.554,.101),(x-.015,1.559,.114),
                (x,1.560,.116),(x+.019,1.555,.105)],.0045,hair)
    # Continuous nose bridge, shaped nostril and small lip contours.
    curved(builder,"Sculpt nasal bridge",
           [(0,1.539,.105),(0,1.519,.114),(0,1.499,.122),
            (0,1.482,.130)],.009,skin,sides=12)
    builder.ellipsoid("Sculpt nose tip",(0,1.479,.138),
                      (.019,.014,.014),skin,18,12)
    for side,sign in (("L",-1),("R",1)):
        builder.ellipsoid("Sculpt nasal ala "+side,
                 (sign*.016,1.473,.126),(.010,.009,.008),skin,14,8)
        builder.ellipsoid("Nostril "+side,
                 (sign*.013,1.464,.131),(.0045,.002,.0025),
                 "#855e50",12,8)
    curved(builder,"Sculpt upper lip",
           [(-.027,1.445,.112),(-.012,1.448,.116),
            (0,1.446,.117),(.012,1.448,.116),(.027,1.445,.112)],
           .0037,"#a57769")
    curved(builder,"Sculpt lower lip",
           [(-.020,1.440,.116),(0,1.438,.120),(.020,1.440,.116)],
           .0030,"#bd8979")
    # Keep the separately sculptable ear meshes; indicate inner anatomy.
    for side,sign in (("L",-1),("R",1)):
        curved(builder,"Sculpt ear helix "+side,
               [(sign*.127,1.532,.020),(sign*.138,1.521,.029),
                (sign*.140,1.499,.031),(sign*.127,1.481,.025)],
               .0038,skin)

def add_hair(builder):
    hair=PALETTES["Ender"]["hair"]
    # Replace smooth cap with a subtly raised crown and swept, tapered,
    # multi-point strands. No generic floating "hair balls."
    builder.ellipsoid("Sculpt hair underlayer",(0,1.614,-.018),
                      (.120,.085,.105),hair,32,16)
    tones=("#354c35","#3d5740","#2d4530")
    for i in range(14):
        t=i/13
        x=-.103+ .206*t
        y=1.662+.012*math.sin(i*1.83)
        z=-.024+.030*(1-abs(2*t-1))
        end_y=1.565 +.018*math.sin(i*2.35)
        pts=[(x,y,z),
             (x-.006,1.657,z+.034),
             (x+.013*math.sin(i),1.633,z+.070),
             (x+.016*math.sin(i+.4),1.603,z+.102),
             (x+.022*math.sin(i+.7),end_y,z+.104)]
        radii=[.009,.012,.013,.010,.0018]
        builder.tube("Hair strand fringe %02d"%i,pts,radii,tones[i%3],sides=9,rough=.95)
    # Tapered sideburn locks avoid the old plastic helmet boundary.
    for side,sign in (("L",-1),("R",1)):
        for j in range(4):
            x=sign*(.104+.004*j)
            pts=[(x,1.645,-.020+.025*j),
                 (x,1.605,-.005+.022*j),
                 (x+sign*.003,1.564,.015+.022*j),
                 (x+sign*.002,1.517+j*.005,.010+.022*j)]
            builder.tube("Hair strand "+side+" side %02d"%j,pts,
                         [.014,.013,.009,.002],tones[j%3],sides=9)
    # Layered hair at nape.
    for j in range(8):
        x=-.093+j*.027
        pts=[(x,1.645,-.08),
             (x,1.61,-.11),(x,1.56,-.108),
             (x*.9,1.51+.01*(j%3),-.095)]
        builder.tube("Hair strand nape %02d"%j,pts,
                     [.012,.013,.009,.0015],tones[j%3],sides=9)

def add_goggles(builder):
    # Two real shallow ring tubes with flush lens inserts; baseline goggles
    # remain a reference and are not "improved" via a bright glow gimmick.
    for sign in (-1,1):
        x=sign*.057
        for band in ("outer","inner"):
            r=.041 if band=="outer" else .034
            z=.124 if band=="outer" else .129
            pts=[(x+r*math.cos(2*math.pi*k/28),
                  1.63+.031*math.sin(2*math.pi*k/28),z)
                 for k in range(29)]
            builder.tube("Sculpt goggle ring %s %s"%(sign,band),pts,
                         .0035 if band=="outer" else .0019,
                         "#bb8951",sides=8,metal=.75,rough=.28)
    # Soft band contour around the visible temples.
    for sign in (-1,1):
        points=[(sign*.092,1.633,.091),(sign*.110,1.634,.045),
                (sign*.105,1.629,-.055)]
        for k in range(len(points)-1):
            builder.tapered("Sculpt goggle side band %s section %d"%(sign,k),
                            points[k],points[k+1],.006,.006,"#49372c")

def add_garment(builder):
    trim="#a98c66"
    # Seams on the existing coat boundary, not separate boxy shoulder pads.
    for sign in (-1,1):
        curved(builder,"Garment waistcoat collar "+str(sign),
               [(sign*.028,1.345,.105),(sign*.058,1.320,.123),
                (sign*.099,1.277,.125),(sign*.092,1.238,.126)],
               .0065,trim)
        curved(builder,"Garment coat side dart "+str(sign),
               [(sign*.155,1.18,.102),(sign*.168,1.11,.102),
                (sign*.155,1.00,.102)],.0036,trim)
    for j in range(5):
        x=-.052+j*.025
        curved(builder,"Garment cuff hand stitch "+str(j),
               [(x,1.075,.062),(x+.009,1.079,.064)],.0025,"#b7a78a",sides=7)

def split_bad_smooth_normal_faces(builder):
    """Local per-triangle normal fix for steep sculpt transitions, no face flips.

    Maintains continuous smooth normals except for a tiny number of triangles
    whose normal is opposite its own oriented surface. Explicitly bounded.
    """
    repaired={}
    new_parts=[]
    for name,vs,ns,faces,mat in builder.parts:
        vs=list(vs);ns=list(ns);faces=list(faces)
        replacements=0
        for fi,(a,b,c) in enumerate(faces):
            u=tuple(vs[b][i]-vs[a][i] for i in range(3))
            v=tuple(vs[c][i]-vs[a][i] for i in range(3))
            n=(u[1]*v[2]-u[2]*v[1],
               u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            length=math.sqrt(sum(x*x for x in n))
            if length<=2e-10:
                raise ValueError(name+": degenerate triangle")
            if sum(n[i]*ns[a][i] for i in range(3)) < -1e-6:
                start=len(vs)
                vs.extend((vs[a],vs[b],vs[c]))
                normal=tuple(x/length for x in n)
                ns.extend((normal,normal,normal))
                faces[fi]=(start,start+1,start+2)
                replacements+=1
        if replacements:
            if replacements>max(12,len(faces)//30):
                raise ValueError(name+": excessive non-smooth corrections")
            repaired[name]=replacements
        new_parts.append((name,vs,ns,faces,mat))
    builder.parts=new_parts
    return repaired

def build(output):
    builder=make("Ender")
    for old in ("Head sculpt","Hair crown","Nose","Mouth",
                "L brow","R brow","Goggle rim -1","Goggle rim 1"):
        replace_part(builder,old,lambda _b: None)
    face_head(builder)
    add_face(builder)
    add_hair(builder)
    add_goggles(builder)
    add_garment(builder)
    if len({p[0] for p in builder.parts})!=len(builder.parts):
        raise ValueError("Nonunique named parts")
    local_normal_fixes=split_bad_smooth_normal_faces(builder)
    output.mkdir(parents=True,exist_ok=True)
    file=output/("Ender_"+VERSION+".glb")
    if file.exists() or (output/"receipt.json").exists():
        raise FileExistsError("Pilot candidate is immutable; choose a fresh output")
    result=builder.save(file)
    receipt={
      "status":"UNRIGGED_NONCANONICAL_FACE_HAIR_STUDY",
      "name":"Ender","version":VERSION,
      "source_builder":"build_cast.py make('Ender')",
      "source_baseline_untouched":True,
      "hair_palette":"temporary existing green palette; exact canon hair color unresolved",
      "approved_original_art_replaced":False,
      "source":result,
      "local_normal_fixes":local_normal_fixes,
      "height_order_canon":"Reson > Aepex > Ender > Ionia > Lyra",
      "limits":["not a creator-approved likeness","no skeletal mesh or animation",
                "no retargeting","no gameplay admission"]
    }
    (output/"receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    return receipt

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(build(args.output),indent=2))
