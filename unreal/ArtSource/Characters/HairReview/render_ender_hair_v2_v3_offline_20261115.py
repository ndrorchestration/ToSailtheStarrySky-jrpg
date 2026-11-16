"""Render the ACTUAL source GLB polygons into an offline diagnostic sheet.

This deliberately lightweight CPU/Pillow preview is NOT Unreal, not a beauty
render, not creator-approved likeness, and does not include a face or goggles.
Painter sorting is approximate and source geometry may intersect; use Unreal
native screenshots before any fit/art claim. Does not rewrite input GLBs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from verify_ender_copper_hair_v2 import glb_document as parse_v2, read_accessor as access_v2
from verify_ender_copper_hair_v3 import parse as parse_v3, access as access_v3

HERE=Path(__file__).resolve().parent
ASSET_V2=HERE/"CandidatesV2/Ender_DarkCopper_LayeredHair_V2_NONCANONICAL.glb"
ASSET_V3=HERE/"CandidatesV3/Ender_BroadLayerHair_V3_NONCANONICAL.glb"
SHA_V2="0da20d3b34e3fdf6171476db1736d2e2607987c71403272207e428f18c8ca9cd"
SHA_V3="bd8286a142294a86784180099db6e8298dc85367632c5a3673fcec50d893d09e"
VIEWS=(
    ("FRONT +Y",(0.,1.,.08)),
    ("3/4 +X +Y",(.72,.90,.17)),
    ("RIGHT +X",(1.,0.,.09)),
    ("REAR -Y",(0.,-1.,.08)),
)
SIDE=480
MARGIN=30


def require(v,msg):
    if not v:
        raise RuntimeError("OFFLINE_HAIR_PREVIEW_FAIL_CLOSED: "+msg)


def unit(a):
    a=np.asarray(a,dtype=float)
    return a/np.linalg.norm(a)


def load(path,expected,v3):
    data=path.read_bytes()
    require(hashlib.sha256(data).hexdigest()==expected,"source GLB SHA mismatch")
    doc,buf=(parse_v3(data) if v3 else parse_v2(data))
    materials=doc["materials"]
    meshes=[]
    for p in doc["meshes"][0]["primitives"]:
        get=(lambda i:access_v3(doc,buf,i)) if v3 else (lambda i:access_v2(doc,buf,i))
        pos=get(p["attributes"]["POSITION"]).astype(float)
        indices=get(p["indices"]).reshape(-1,3)
        rgba=materials[p["material"]]["pbrMetallicRoughness"]["baseColorFactor"][:3]
        color=np.power(np.clip(rgba,0,1),1/2.2)*255
        meshes.append((pos,indices,color))
    require(len(meshes)==(4 if v3 else 5),"unexpected material count")
    bounds=np.concatenate([p for p,_,_ in meshes],axis=0)
    return meshes,bounds


def frame(meshes,bounds,camera,title):
    view=unit(camera)
    right=unit(np.cross(view,[0.,0.,1.]))
    up=unit(np.cross(right,view))
    center=(bounds.max(axis=0)+bounds.min(axis=0))*.5
    proj=np.stack((bounds@right,bounds@up),axis=1)
    reach=float(np.max(proj.max(axis=0)-proj.min(axis=0)))
    scale=(SIDE-2*MARGIN)/(reach*1.25)
    scale=min(scale,1750.)
    frame=Image.new("RGB",(SIDE,SIDE),(33,37,43))
    draw=ImageDraw.Draw(frame)
    # Geometry only, all five original material groups preserved in the V2 file.
    polygons=[]
    for pos,faces,color in meshes:
        v=pos-center
        coords=np.stack((v@right,v@up),axis=1)
        pixels=np.stack((SIDE*.5+coords[:,0]*scale,
                          SIDE*.55-coords[:,1]*scale),axis=1)
        for ix in faces:
            tri=v[ix]
            normal=np.cross(tri[1]-tri[0],tri[2]-tri[0])
            norm=float(np.linalg.norm(normal))
            if norm<1e-12:
                continue
            n=normal/norm
            # Simple two-sided ambient/lambert material; DOES NOT certify PBR.
            illumination=.54+.39*max(0.,float(np.dot(n,unit((.3,.85,.6)))))
            rgb=tuple(int(np.clip(c*illumination,0,255)) for c in color)
            pts=[tuple(round(float(x),2) for x in xy) for xy in pixels[ix]]
            depth=float(np.mean(tri@view))
            polygons.append((depth,pts,rgb))
    polygons.sort(key=lambda x:x[0])  # Painters' depth sorting, offline only.
    for _,pts,color in polygons:
        draw.polygon(pts,fill=color)
    draw.text((16,14),title,fill=(239,239,233))
    draw.text((16,SIDE-27),"ACTUAL SOURCE MESH / NO FACE / NO UE",fill=(179,182,181))
    return frame


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir",required=True,type=Path)
    args=ap.parse_args()
    out=args.outdir.resolve()
    require(out.is_dir(),"output directory must already exist")
    target=out/"EnderHair_V2_vs_V3_OFFLINE_SOURCE_MESH_SHEET.png"
    receipt=out/"EnderHair_V2_vs_V3_OFFLINE_SOURCE_MESH_RECEIPT.json"
    require(not target.exists() and not receipt.exists(),"never overwrite comparison evidence")
    v2,bounds2=load(ASSET_V2,SHA_V2,False)
    v3,bounds3=load(ASSET_V3,SHA_V3,True)
    width=SIDE*4
    sheet=Image.new("RGB",(width,SIDE*2+104),(24,27,31))
    draw=ImageDraw.Draw(sheet)
    draw.text((16,11),"ENDER HAIR V2 vs V3 / ACTUAL GLB GEOMETRY / OFFLINE CPU DIAGNOSTIC",fill=(242,242,241))
    draw.text((16,33),"NOT UNREAL - NOT FACIAL OR GOGGLE FIT - NOT AN ART APPROVAL",fill=(243,194,107))
    for row,(name,meshes,bounds) in enumerate((("V2 TUBULAR REJECTED",v2,bounds2),
                                               ("V3 BROAD-LAYER STUDY",v3,bounds3))):
        for col,(label,camera) in enumerate(VIEWS):
            sheet.paste(frame(meshes,bounds,camera,name+" / "+label),
                        (SIDE*col,56+SIDE*row))
    draw.text((16,56+SIDE*2+8),
              "Current creator-approved Ender portrait remains authoritative; both are NONCANONICAL studies.",
              fill=(212,216,220))
    sheet.save(target,optimize=True)
    result={"status":"OFFLINE_SOURCE_3D_PREVIEW_ONLY_NOT_UNREAL",
            "preview_sha256":hashlib.sha256(target.read_bytes()).hexdigest(),
            "preview_dimensions_px":list(sheet.size),
            "source_v2_sha256":SHA_V2,
            "source_v3_sha256":SHA_V3,
            "angles":[x[0] for x in VIEWS],
            "native_unreal":False,"creator_approved":False,
            "face_goggle_fit_verified":False,"animation_verified":False,
            "source_meshes_modified":False}
    receipt.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))


if __name__=="__main__":
    main()
