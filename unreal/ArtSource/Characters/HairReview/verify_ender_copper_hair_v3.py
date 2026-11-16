"""Independent engine-free validation of Ender V3 original static hair lookdev.

A source pass is never native UE import, head/goggle fit, animation or art approval.
"""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ASSET = HERE / "CandidatesV3/Ender_BroadLayerHair_V3_NONCANONICAL.glb"
MATERIALS = ("UmberRootShell", "DeepChestnutVolumes",
             "WarmCopperPlanes", "SoftDarkUnderlayers")


def require(value, label):
    if not value:
        raise ValueError("V3_FAIL_CLOSED: " + label)


def parse(data):
    require(len(data)>64, "short GLB")
    sig, version, full=struct.unpack_from("<4sII",data)
    require(sig==b"glTF" and version==2 and full==len(data),"GLB signature/version/length")
    jslen, jstag=struct.unpack_from("<I4s",data,12)
    require(jstag==b"JSON" and jslen%4==0 and jslen>64,"JSON chunk")
    require(20+jslen+8<=len(data),"JSON bounds")
    doc=json.loads(data[20:20+jslen])
    binlen,bintag=struct.unpack_from("<I4s",data,20+jslen)
    require(bintag==b"BIN\x00" and binlen%4==0,"BIN chunk")
    start=28+jslen
    require(start+binlen==len(data),"BIN parity")
    require(doc["buffers"]==[{"byteLength":binlen}],"buffer parity")
    return doc,memoryview(data)[start:]


def access(doc,binary,n):
    a=doc["accessors"][n]
    v=doc["bufferViews"][a["bufferView"]]
    require(v["buffer"]==0,"single buffer")
    dtype={5126:np.float32,5125:np.uint32}.get(a["componentType"])
    require(dtype is not None,"type")
    width={"VEC3":3,"SCALAR":1}.get(a["type"])
    require(width is not None,"width")
    count=a["count"]
    start=v.get("byteOffset",0)+a.get("byteOffset",0)
    end=start+count*width*np.dtype(dtype).itemsize
    require(count>0 and end<=len(binary) and
            end<=v["byteOffset"]+v["byteLength"],"accessor span")
    return np.frombuffer(binary[start:end],dtype=dtype).reshape((count,width))


def inspect(data):
    doc,buf=parse(data)
    extras=doc.get("extras",{})
    require(extras.get("review_only") is True and
            extras.get("source_authored") is True,"source gate")
    for field in ("creator_approved","head_fit_verified","native_render_verified",
                  "animation","rigged","groom","gameplay_asset",
                  "user_reference_pixels_included"):
        require(extras.get(field) is False,"false-promotion field "+field)
    require("skins" not in doc and "animations" not in doc,
            "must remain static study")
    require(len(doc["meshes"])==1 and len(doc["nodes"])==1,"one static mesh")
    prims=doc["meshes"][0]["primitives"]
    require(len(prims)==4 and len(doc["materials"])==4,"four broad material groups")
    require(tuple(m["name"] for m in doc["materials"])==MATERIALS,"palette lock")
    require(all(m["pbrMetallicRoughness"]["metallicFactor"]==0.
                for m in doc["materials"]),"hair cannot be metallic")
    triangle_total=0
    positions=[]
    for k,p in enumerate(prims):
        require(p.get("material")==k and p.get("mode")==4,"primitive/material")
        v=access(doc,buf,p["attributes"]["POSITION"]).astype(np.float64)
        n=access(doc,buf,p["attributes"]["NORMAL"]).astype(np.float64)
        f=access(doc,buf,p["indices"]).flatten()
        require(len(v)==len(n) and len(f)%3==0 and
                np.max(f)<len(v),"index/attribute parity")
        require(np.isfinite(v).all() and np.isfinite(n).all(),"finite positions/normals")
        require(np.all(np.abs(np.linalg.norm(n,axis=1)-1.)<.02),"unit normals")
        tris=v[f.reshape(-1,3)]
        cross=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0])
        area=np.linalg.norm(cross,axis=1)
        require(np.min(area)>1e-12,"nondegenerate triangles")
        if k==0:
            # The outward-facing scalp shell must not be inverted.
            center=np.mean(tris,axis=1)
            geometric=np.sum(cross*center,axis=1)
            require(float((geometric>0).mean())>.98,"scalp shell outward winding")
        triangle_total+=len(tris)
        positions.append(v)
    require(25000<=triangle_total<=40000,"bounded authored surface count")
    pts=np.concatenate(positions)
    dims=(np.max(pts,axis=0)-np.min(pts,axis=0))*100.
    require(np.all(dims>np.array([15.,15.,12.])) and
            np.all(dims<np.array([32.,33.,32.])),"provisional scalp-sized bounds")
    return {"status":"SOURCE_GEOMETRY_PASS_ART_HOLD",
            "sha256":hashlib.sha256(data).hexdigest(),
            "triangles":triangle_total,"materials":len(prims),
            "dimensions_cm":[round(float(x),4) for x in dims],
            "native_unreal":False,"fit_verified":False,"creator_approved":False}


if __name__=="__main__":
    print(json.dumps(inspect(ASSET.read_bytes()),sort_keys=True,indent=2))
