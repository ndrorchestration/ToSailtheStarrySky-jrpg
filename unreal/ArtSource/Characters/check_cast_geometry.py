"""Independent stdlib glTF geometry gate for static cast review assets.

This catches zero-area faces, inward surfaces, invalid indices, nonfinite
normals, and stale generated files. It is not a substitute for Unreal import.
"""
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Candidates" if (ROOT / "Candidates").exists() else ROOT / "out"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def vector(values):
    return tuple(float(v) for v in values)


def cross(a, b):
    return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def check_one(path, record):
    data = path.read_bytes()
    require(data[:4] == b"glTF" and len(data) >= 28, path.name+": GLB header")
    require(struct.unpack_from("<II", data, 4) == (2, len(data)), path.name+": GLB length")
    json_len, json_type = struct.unpack_from("<I4s", data, 12)
    require(json_type == b"JSON" and json_len % 4 == 0, path.name+": JSON chunk")
    doc = json.loads(data[20:20+json_len])
    buffer_len, buffer_type = struct.unpack_from("<I4s", data, 20+json_len)
    start = 28+json_len
    require(buffer_type == b"BIN\x00" and start+buffer_len == len(data), path.name+": BIN chunk")
    require(hashlib.sha256(data).hexdigest() == record["sha256"], path.name+": SHA-256")
    require(len(doc["meshes"]) == 1 and len(doc["nodes"]) == 1 and not doc.get("skins"), path.name+": one static mesh")
    mesh = doc["meshes"][0]
    require(len(mesh["primitives"]) == record["material_sections"], path.name+": material sections")
    parts = mesh["extras"]["partMap"]
    require(len(parts) == record["mesh_parts"], path.name+": part map")

    def accessor(index):
        a = doc["accessors"][index]
        view = doc["bufferViews"][a["bufferView"]]
        require(view["buffer"] == 0, path.name+": buffer reference")
        fmt = {5126:"f", 5123:"H"}[a["componentType"]]
        cols = {"VEC3":3,"SCALAR":1}[a["type"]]
        size = struct.calcsize("<"+fmt*cols)
        begin = start+view["byteOffset"]+a.get("byteOffset",0)
        require(view["byteOffset"]+a.get("byteOffset",0)+a["count"]*size <= buffer_len,
                path.name+": accessor range")
        values = [struct.unpack_from("<"+fmt*cols,data,begin+i*size) for i in range(a["count"])]
        return a, values

    triangles = 0
    for primitive in mesh["primitives"]:
        mat = primitive["material"]
        require(0 <= mat < len(doc["materials"]), path.name+": material reference")
        pa, positions = accessor(primitive["attributes"]["POSITION"])
        _, normals = accessor(primitive["attributes"]["NORMAL"])
        _, indices = accessor(primitive["indices"])
        require(len(positions) == len(normals) and len(indices) % 3 == 0, path.name+": attribute/index count")
        require(all(math.isfinite(v) for point in positions+normals for v in point), path.name+": nonfinite geometry")
        require(all(abs(math.sqrt(dot(n,n))-1) < .02 for n in normals), path.name+": unnormalized normal")
        for axis in range(3):
            lo = min(p[axis] for p in positions)
            hi = max(p[axis] for p in positions)
            require(abs(lo-pa["min"][axis]) < 1e-6 and abs(hi-pa["max"][axis]) < 1e-6,
                    path.name+": accessor bounds")
        mapped = [part for part in parts if part["material"] == mat]
        spans = [(part["firstVertex"],part["firstVertex"]+part["vertexCount"]) for part in mapped]
        require(spans and spans[0][0] == 0 and spans[-1][1] == len(positions) and
                all(a[1] == b[0] for a,b in zip(spans,spans[1:])),path.name+": part spans")
        centers=[]
        for begin,end in spans:
            segment = positions[begin:end]
            centers.append(tuple((min(p[axis] for p in segment)+max(p[axis] for p in segment))/2
                                 for axis in range(3)))
        for i in range(0,len(indices),3):
            a,b,c = (indices[i+k][0] for k in range(3))
            require(max(a,b,c) < len(positions),path.name+": index outside vertex array")
            part = next((k for k,(begin,end) in enumerate(spans) if begin <= a < end),None)
            require(part is not None and all(spans[part][0] <= x < spans[part][1] for x in (b,c)),
                    path.name+": triangle crosses part boundary")
            edge1=sub(positions[b],positions[a]);edge2=sub(positions[c],positions[a])
            face=cross(edge1,edge2)
            require(dot(face,face) > 4e-20,path.name+": zero-area triangle")
            require(dot(face,normals[a]) >= -1e-6,path.name+": face/normal mismatch")
            middle=tuple((positions[a][axis]+positions[b][axis]+positions[c][axis])/3 for axis in range(3))
            require(dot(face,sub(middle,centers[part])) >= -1e-9,path.name+": inward face")
            triangles+=1
    return triangles


def main():
    records=json.loads((SOURCE/"manifest.json").read_text(encoding="utf-8"))["characters"]
    require(tuple(r["name"] for r in records) == ("Ender","Ionia","Lyra","Reson","Aepex"),"cast identity order")
    for r in records:
        count=check_one(SOURCE/(r["name"]+".glb"),r)
        print("CAST_GEOMETRY_PASS",r["name"],count,"triangles")


if __name__ == "__main__":
    main()
