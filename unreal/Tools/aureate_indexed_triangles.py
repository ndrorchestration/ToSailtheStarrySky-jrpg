"""Validated triangle-index decoder for immutable review GLBs.

Vertices themselves are decoded by audit_aureate_wing_clearance.read_vertices.
Never process an unverified asset with this narrow-phase preview tool.
"""
from __future__ import annotations

import json
import struct
from pathlib import Path


def read_triangles(path: Path):
    raw=path.read_bytes()
    if len(raw)<32 or raw[:4]!=b"glTF" or struct.unpack_from("<I",raw,4)[0]!=2:
        raise ValueError("Invalid review GLB header")
    if struct.unpack_from("<I",raw,8)[0]!=len(raw):
        raise ValueError("GLB size mismatch")
    jlen,jtype=struct.unpack_from("<I4s",raw,12)
    if jtype!=b"JSON" or jlen<4 or jlen%4 or 28+jlen>len(raw):
        raise ValueError("Invalid JSON chunk")
    doc=json.loads(raw[20:20+jlen])
    bin_start=28+jlen
    blen,btype=struct.unpack_from("<I4s",raw,bin_start-8)
    if btype!=b"BIN\0" or blen%4 or bin_start+blen!=len(raw):
        raise ValueError("Invalid BIN chunk")
    bufs=doc.get("buffers")
    if (not isinstance(bufs,list) or len(bufs)!=1 or
        type(bufs[0].get("byteLength")) is not int):
        raise ValueError("Missing declared logical buffer")
    logical_length=bufs[0]["byteLength"]
    if logical_length<0 or logical_length>blen or blen-logical_length>3:
        raise ValueError("Invalid declared logical buffer")
    logical_end=bin_start+logical_length
    meshes=doc.get("meshes")
    if not isinstance(meshes,list) or len(meshes)!=1:
        raise ValueError("Expected one mesh")
    faces=[];offset=0
    for prim in meshes[0]["primitives"]:
        if prim.get("mode")!=4 or "indices" not in prim:
            raise ValueError("Only indexed triangles supported")
        acc=doc["accessors"][prim["indices"]]
        count=acc["count"]
        if (acc.get("componentType")!=5125 or acc.get("type")!="SCALAR" or
            type(count) is not int or count<=0 or count%3 or count>300000 or
            "sparse" in acc):
            raise ValueError("Invalid triangle index accessor")
        view=doc["bufferViews"][acc["bufferView"]]
        vo=view.get("byteOffset",0);ao=acc.get("byteOffset",0);size=view["byteLength"]
        if (view.get("buffer")!=0 or
            any(type(x) is not int for x in (vo,ao,size)) or
            vo<0 or ao<0 or size<0 or vo%4 or ao%4 or
            bin_start+vo+size>logical_end or ao+count*4>size or
            view.get("byteStride",4)!=4):
            raise ValueError("Triangle indices exceed declared view")
        p=doc["accessors"][prim["attributes"]["POSITION"]]
        positions=p["count"]
        if type(positions) is not int or positions<=0:
            raise ValueError("Invalid primitive position count")
        start=bin_start+vo+ao
        for i,j,k in struct.iter_unpack("<III",raw[start:start+count*4]):
            if max(i,j,k)>=positions:
                raise ValueError("Out-of-range primitive triangle index")
            faces.append((i+offset,j+offset,k+offset))
        offset+=positions
    return faces
