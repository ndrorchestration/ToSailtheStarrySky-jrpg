#!/usr/bin/env python3
"""Read-only complete-vertex/index geometry audit for Aureate Wake V2 GLBs.

Audits ACTUAL GLB binary buffers instead of trusting glTF accessor min/max.
No third-party packages, Unreal import, actor binding, game writes, or art approval.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from build_aureate_fidelity_v2 import FILES
from import_aureate_fidelity_v2 import inspect

MAX_BYTES = 10_000_000
MAX_VERTICES_PER_PRIMITIVE = 200_000
TOL = 3e-5  # metre units; accommodates rounded float32 extrema

class GeometryHold(ValueError):
    pass


def parse_glb(data:bytes):
    if not 36 <= len(data) <= MAX_BYTES or data[:4] != b"glTF":
        raise GeometryHold("Invalid/oversized GLB")
    version, total=struct.unpack_from("<II",data,4)
    if version!=2 or total!=len(data):
        raise GeometryHold("Incorrect GLB version/length")
    jlen,jtype=struct.unpack_from("<I4s",data,12)
    if jtype!=b"JSON" or jlen%4 or 20+jlen+8>len(data):
        raise GeometryHold("Bad JSON chunk")
    blen,btype=struct.unpack_from("<I4s",data,20+jlen)
    if btype!=b"BIN\0" or blen%4 or 28+jlen+blen!=len(data):
        raise GeometryHold("Bad BIN chunk")
    try:
        doc=json.loads(data[20:20+jlen])
    except (UnicodeError,ValueError) as exc:
        raise GeometryHold("Invalid GLB JSON") from exc
    if not isinstance(doc,dict):
        raise GeometryHold("Invalid glTF document")
    return doc,memoryview(data)[28+jlen:]


def accessor_values(doc:dict, blob:memoryview, index:int, *, width:int, ctype:int, target:int):
    try:
        acc=doc["accessors"][index]
        view=doc["bufferViews"][acc["bufferView"]]
        count=acc["count"]
        comps={"VEC2":2,"VEC3":3,"SCALAR":1}[acc["type"]]
        if not isinstance(count,int) or not 1<=count<=MAX_VERTICES_PER_PRIMITIVE*3:
            raise GeometryHold("Unsafe accessor count")
        if acc["componentType"]!=ctype or comps!=width or view["target"]!=target:
            raise GeometryHold("Unsupported attribute/indices layout")
        if view["buffer"]!=0 or acc.get("normalized",False) or "sparse" in acc:
            raise GeometryHold("Unsupported sparse/normalized buffer")
        size=4*width
        stride=view.get("byteStride",size)
        if stride!=size:
            raise GeometryHold("Unexpected stride")
        origin=view.get("byteOffset",0)+acc.get("byteOffset",0)
        vstart=view.get("byteOffset",0)
        vend=vstart+view["byteLength"]
        end=origin+(count-1)*stride+size
        if (min(origin,vstart)<0 or end>vend or vend>len(blob) or
                origin%4 or vstart%4):
            raise GeometryHold("Accessor escapes binary buffer view")
        fmt="<"+("f" if ctype==5126 else "I")*width
        values=[struct.unpack_from(fmt,blob,origin+i*stride) for i in range(count)]
    except (KeyError,IndexError,TypeError,ValueError,struct.error) as exc:
        if isinstance(exc,GeometryHold):raise
        raise GeometryHold("Invalid accessor/bin layout") from exc
    if ctype==5126 and not all(math.isfinite(x) for row in values for x in row):
        raise GeometryHold("Nonfinite mesh vertex/normal/UV")
    return values, acc


def span_and_minmax_match(positions:list,acc:dict):
    if "min" not in acc or "max" not in acc:
        raise GeometryHold("Missing required position extrema")
    for axis in range(3):
        try:
            actual_min=min(row[axis] for row in positions)
            actual_max=max(row[axis] for row in positions)
            claimed_min=float(acc["min"][axis]);claimed_max=float(acc["max"][axis])
        except (KeyError,IndexError,TypeError,ValueError) as exc:
            raise GeometryHold("Malformed accessor extrema") from exc
        if not all(math.isfinite(x) for x in (claimed_min,claimed_max)):
            raise GeometryHold("Nonfinite claimed extrema")
        if abs(actual_min-claimed_min)>TOL or abs(actual_max-claimed_max)>TOL:
            raise GeometryHold("Claimed accessor bounds disagree with actual vertices")


def audit_binary(data:bytes, *, expected_name:str) ->dict:
    doc,blob=parse_glb(data)
    if expected_name not in FILES:
        raise GeometryHold("Unrecognized V2 review candidate")
    kind=FILES.index(expected_name)
    if (doc.get("asset",{}).get("version")!="2.0" or len(doc.get("nodes",[]))!=1
        or doc["nodes"][0].get("mesh")!=0 or
        any(k in doc["nodes"][0] for k in ("matrix","translation","rotation","scale"))
        or len(doc.get("meshes",[]))!=1 or len(doc["meshes"][0].get("primitives",[]))!=3
        or len(doc.get("materials",[]))!=3 or len(doc.get("buffers",[]))!=1
        or doc["buffers"][0].get("byteLength")!=len(blob)):
        raise GeometryHold("Unexpected model topology/node transformation")
    extras=doc.get("extras",{})
    if (extras.get("authority")!="NONCANONICAL_REVIEW_NOT_ART_ACCEPTED"
        or extras.get("sourceToGltfScale")!=.01
        or extras.get("axisRemap")!="UE_X_FORWARD_Z_UP_TO_GLTF_Y_UP"):
        raise GeometryHold("Incorrect provenance/scale/orientation")
    if kind==1 and doc["materials"][0].get("alphaMode")!="BLEND":
        raise GeometryHold("Bridge glass alpha provenance lost")
    x_all=[];y_all=[];z_all=[]
    triangles=0;min_normal_dot=1.0
    for n,prim in enumerate(doc["meshes"][0]["primitives"]):
        if prim.get("material")!=n or prim.get("mode")!=4:
            raise GeometryHold("Unexpected primitive material/triangle type")
        attrs=prim.get("attributes",{})
        pos,posmeta=accessor_values(doc,blob,attrs["POSITION"],width=3,ctype=5126,target=34962)
        normals,_=accessor_values(doc,blob,attrs["NORMAL"],width=3,ctype=5126,target=34962)
        uv,_=accessor_values(doc,blob,attrs["TEXCOORD_0"],width=2,ctype=5126,target=34962)
        indices,_=accessor_values(doc,blob,prim["indices"],width=1,ctype=5125,target=34963)
        if not (len(pos)==len(normals)==len(uv)) or len(pos)>MAX_VERTICES_PER_PRIMITIVE:
            raise GeometryHold("Position/normal/UV count mismatch")
        if len(indices)%3 or len(indices)<3:
            raise GeometryHold("Index count not triangular")
        span_and_minmax_match(pos,posmeta)
        x_all.extend(p[0] for p in pos);y_all.extend(p[1] for p in pos);z_all.extend(p[2] for p in pos)
        for (ia,),(ib,),(ic,) in zip(indices[::3],indices[1::3],indices[2::3]):
            if max(ia,ib,ic)>=len(pos) or len({ia,ib,ic})!=3:
                raise GeometryHold("Out-of-range/repeated triangle index")
            a,b,c=pos[ia],pos[ib],pos[ic]
            ab=[b[i]-a[i] for i in range(3)]
            ac=[c[i]-a[i] for i in range(3)]
            face=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
            norm_sq=sum(x*x for x in face)
            if norm_sq<1e-16:
                raise GeometryHold("Zero-area/degenerate triangle")
            inv=1/math.sqrt(norm_sq)
            unit=[x*inv for x in face]
            for idx in (ia,ib,ic):
                vertex_normal=normals[idx]
                mag=math.sqrt(sum(x*x for x in vertex_normal))
                if not .99<mag<1.01:
                    raise GeometryHold("Invalid vertex normal length")
                alignment=sum(unit[i]*vertex_normal[i] for i in range(3))/mag
                if alignment<.98:
                    raise GeometryHold("Triangle winding/normal mismatch")
                min_normal_dot=min(min_normal_dot,alignment)
            triangles+=1
    if not triangles or not x_all:
        raise GeometryHold("Empty review mesh")
    span=(max(x_all)-min(x_all),max(y_all)-min(y_all),max(z_all)-min(z_all))
    # glTF Y-up: dimensions here are X-longitudinal, Y-vertical, Z-port/starboard.
    ranges=(((7.90,8.05),(.60,1.35),(1.40,2.60)),
            ((1.75,1.98),(1.0,1.45),(.90,1.3)))
    if any(not low<value<high for value,(low,high) in zip(span,ranges[kind])):
        raise GeometryHold("Actual mesh coordinates exceed review envelope or have wrong axis")
    return {
        "asset":expected_name,
        "sha256":hashlib.sha256(data).hexdigest(),
        "triangle_count":triangles,
        "complete_binary_vertex_coverage":True,
        "max_abs_normal_deviation":round(1-min_normal_dot,8),
        "actual_dimensions_gltf_m":[round(v,5) for v in span],
        "native_unreal_import":"NOT_ESTABLISHED",
        "creator_model_approval":"NOT_ESTABLISHED",
    }


def audit_folder(folder:Path) ->dict:
    # Existing preflight enforces exact deterministic bytes + manifest SHA.
    provenance=inspect(folder)
    output=[]
    for name in FILES:
        p=folder/name
        if not p.is_file() or p.is_symlink():
            raise GeometryHold("Missing/symlinked review GLB")
        output.append(audit_binary(p.read_bytes(),expected_name=name))
    return {"status":"COMPLETE_GLTF_BUFFER_GEOMETRY_PASS_OFFLINE_ONLY",
            "source_sha256":provenance["approved_image_sha256"],
            "candidate_reports":output,
            "orbiter_unlocked":False,
            "native_art_approved":False}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--folder",required=True,type=Path)
    args=p.parse_args(argv)
    try:
        print(json.dumps(audit_folder(args.folder),indent=2,sort_keys=True))
    except (GeometryHold,ValueError,OSError,KeyError,TypeError) as exc:
        p.exit(1,"GEOMETRY AUDIT HOLD: "+str(exc)+"\n")


if __name__=="__main__":
    main()
