"""Strict source-only binary GLB validation; never claims native Unreal or art approval."""
import hashlib
import json
import struct
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
CANDIDATE = HERE / "CandidatesV2/Ender_DarkCopper_LayeredHair_V2_NONCANONICAL.glb"
EXPECTED = "0da20d3b34e3fdf6171476db1736d2e2607987c71403272207e428f18c8ca9cd"
MATERIALS = [
    "DeepCopperRoots", "WarmChestnutBase", "TousledAuburnBody",
    "CopperRimHighlights", "ShadowBrownStrands"
]

def require(value, msg):
    if not value:
        raise AssertionError("FAIL_CLOSED " + msg)

def glb_document(data):
    require(len(data) >= 32, "short GLB")
    sig, version, total = struct.unpack_from("<4sII", data, 0)
    require(sig == b"glTF" and version == 2 and total == len(data), "GLB header")
    length, tag = struct.unpack_from("<I4s", data, 12)
    require(tag == b"JSON" and length%4 == 0, "JSON chunk")
    require(20 + length + 8 <= len(data), "JSON bounds")
    document = json.loads(data[20:20+length])
    bin_count, bin_tag = struct.unpack_from("<I4s", data, 20+length)
    require(bin_tag == b"BIN\x00", "binary chunk tag")
    start = 20 + length + 8
    require(start+bin_count == len(data) and bin_count%4 == 0, "binary chunk size")
    require(document["buffers"][0]["byteLength"] == bin_count, "buffer span parity")
    return document, memoryview(data)[start:]

def read_accessor(doc, buf, idx):
    accessor = doc["accessors"][idx]
    view = doc["bufferViews"][accessor["bufferView"]]
    require(view["buffer"] == 0, "single buffer")
    kind = accessor["componentType"]
    sizes = {5126:(np.float32,4),5125:(np.uint32,4)}
    require(kind in sizes, "accessor type")
    comps = {"VEC3":3,"SCALAR":1}
    require(accessor["type"] in comps, "accessor width")
    n = accessor["count"]
    width = comps[accessor["type"]]
    byte_start = view.get("byteOffset",0) + accessor.get("byteOffset",0)
    byte_end = byte_start + n*width*sizes[kind][1]
    require(n>0 and byte_end <= len(buf) and byte_end <= view["byteOffset"]+view["byteLength"],
            "accessor bounds")
    return np.frombuffer(buf[byte_start:byte_end],dtype=sizes[kind][0]).reshape(n,width)

def verify_bytes(data, require_sha=False):
    if require_sha:
        require(hashlib.sha256(data).hexdigest() == EXPECTED, "pinned source GLB SHA-256")
    doc, binary = glb_document(data)
    require(doc.get("scene")==0 and len(doc.get("scenes",[]))==1,
            "single scene")
    require(len(doc.get("meshes",[]))==1 and len(doc["meshes"][0]["primitives"])==5,
            "five-material hair mesh")
    require(len(doc.get("materials",[]))==5, "exact 5 PBR palettes")
    require([m["name"] for m in doc["materials"]]==MATERIALS, "material lock")
    require(doc.get("skins") is None and doc.get("animations") is None,
            "not a false skeletal mesh/groom")
    extras = doc.get("extras", {})
    for key in ("review_only","source_authored"):
        require(extras.get(key) is True, key+" must be true")
    for key in ("creator_approved","actual_head_fit_verified","gameplay_asset","rigged","groom"):
        require(extras.get(key) is False, key+" must be false")
    require(extras.get("source_reference_pixels_included") is False, "private references excluded")
    all_bounds = []
    tris = 0
    material_ids = set()
    for primitive in doc["meshes"][0]["primitives"]:
        require(primitive.get("mode")==4, "triangles only")
        material = primitive["material"]
        require(material not in material_ids and 0 <= material < 5, "unique material IDs")
        material_ids.add(material)
        pos = read_accessor(doc,binary,primitive["attributes"]["POSITION"]).astype(np.float64)
        norm = read_accessor(doc,binary,primitive["attributes"]["NORMAL"]).astype(np.float64)
        idx = read_accessor(doc,binary,primitive["indices"]).flatten()
        require(len(pos)==len(norm) and len(idx)%3==0, "position/normal/triangle parity")
        require(np.all(idx < len(pos)), "index bounds")
        require(np.isfinite(pos).all() and np.isfinite(norm).all(), "all vertices finite")
        unit = np.linalg.norm(norm,axis=1)
        require(np.all((.99 < unit) & (unit < 1.01)), "vertex normals unit length")
        faces = pos[idx.reshape(-1,3)]
        area = np.linalg.norm(np.cross(faces[:,1]-faces[:,0],
                                       faces[:,2]-faces[:,0]),axis=1)
        require(np.min(area) > 1e-12, "every face nonzero")
        tris += len(faces)
        all_bounds.append((np.min(pos,axis=0),np.max(pos,axis=0)))
    require(material_ids == set(range(5)), "all five materials used")
    require(27000 <= tris < 30000, "expected bounded triangle count")
    mins = np.min([x[0] for x in all_bounds],axis=0)
    maxs = np.max([x[1] for x in all_bounds],axis=0)
    dims = (maxs - mins)*100
    require(np.all((dims > [20,20,16])&(dims < [28,30,24])),
            "review hair scale sanity")
    return {"status":"SOURCE_HAIR_GLTF_GEOMETRY_VALID_NONCANONICAL",
            "sha256":hashlib.sha256(data).hexdigest(),
            "materials":len(material_ids),"triangles":tris,
            "dimensions_cm":np.round(dims,3).tolist(),
            "native_unreal_render":False,"creator_approval":False}

def run():
    return verify_bytes(CANDIDATE.read_bytes(),require_sha=True)

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,indent=2))
