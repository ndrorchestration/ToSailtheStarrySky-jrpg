"""Independent strict geometry validation for curved, nonconvex Ender lookdev.

Baseline check_cast_geometry.py uses a convex-center heuristic. That is valid
for legacy primitive parts but not for sculpted curved hair tubes/garment seams.
Do NOT relax or edit the baseline checker. Validate real triangles and normals.
"""
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

def check(glb, receipt, required_parts=None):
    glb=Path(glb)
    raw=glb.read_bytes()
    assert len(raw)>=28 and raw[:4]==b"glTF"
    version,size=struct.unpack_from("<II",raw,4)
    assert version==2 and size==len(raw)
    assert hashlib.sha256(raw).hexdigest()==receipt["source"]["sha256"]
    js_len,kind=struct.unpack_from("<I4s",raw,12)
    assert kind==b"JSON" and js_len%4==0
    doc=json.loads(raw[20:20+js_len])
    start=28+js_len
    bin_len,kind=struct.unpack_from("<I4s",raw,20+js_len)
    assert kind==b"BIN\0" and start+bin_len==len(raw)
    assert len(doc["meshes"])==1 and len(doc["nodes"])==1
    assert not doc.get("skins") and not doc.get("animations")
    mesh=doc["meshes"][0]
    assert len(mesh["primitives"])==receipt["source"]["material_sections"]
    parts=mesh["extras"]["partMap"]
    assert len(parts)==receipt["source"]["mesh_parts"]
    assert len({p["name"] for p in parts})==len(parts)
    assert not any(p["vertexCount"]<3 for p in parts)
    if required_parts is None:
        required_parts = ("Sculpt face with jaw","Sculpt nose tip","Sculpt nasal bridge",
                          "Sculpt upper lip","Sculpt goggle ring -1 outer",
                          "Sculpt hair underlayer","Hair strand fringe 00")
    for key in required_parts:
        assert key in {p["name"] for p in parts}, "Missing detail: "+key

    def fetch(index):
        a=doc["accessors"][index]
        view=doc["bufferViews"][a["bufferView"]]
        assert view["buffer"]==0 and "sparse" not in a
        fmt={5126:"f",5123:"H"}[a["componentType"]]
        components={"VEC3":3,"SCALAR":1}[a["type"]]
        form="<"+fmt*components
        step=struct.calcsize(form)
        rel=view["byteOffset"]+a.get("byteOffset",0)
        assert rel+a["count"]*step<=bin_len
        return [struct.unpack_from(form,raw,start+rel+j*step) for j in range(a["count"])]
    total=0
    nonconvex_parts=0
    for prim in mesh["primitives"]:
        mat=prim["material"]
        assert 0<=mat<len(doc["materials"])
        positions=fetch(prim["attributes"]["POSITION"])
        normals=fetch(prim["attributes"]["NORMAL"])
        indices=[x[0] for x in fetch(prim["indices"])]
        assert len(positions)==len(normals) and len(indices)%3==0
        assert all(math.isfinite(v) for vec in positions+normals for v in vec)
        assert all(abs(math.sqrt(sum(c*c for c in n))-1)<.02 for n in normals)
        mapping=[p for p in parts if p["material"]==mat]
        assert mapping
        spans=[(p["firstVertex"],p["firstVertex"]+p["vertexCount"]) for p in mapping]
        assert spans[0][0]==0 and spans[-1][1]==len(positions)
        assert all(a[1]==b[0] for a,b in zip(spans,spans[1:]))
        for j in range(0,len(indices),3):
            a,b,c=indices[j:j+3]
            assert max(a,b,c)<len(positions) and min(a,b,c)>=0
            part=next((k for k,(start,end) in enumerate(spans) if start<=a<end),None)
            assert part is not None and all(spans[part][0]<=k<spans[part][1] for k in (a,b,c))
            u=tuple(positions[b][z]-positions[a][z] for z in range(3))
            v=tuple(positions[c][z]-positions[a][z] for z in range(3))
            cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
            area=sum(c*c for c in cross)
            assert area>4e-20, "Degenerate triangle in "+mapping[part]["name"]
            for idx in (a,b,c):
                assert sum(cross[k]*normals[idx][k] for k in range(3))>=-1e-6, (
                    "Reversed vertex normal in "+mapping[part]["name"])
            total+=1
    assert total>10000, "Unexpectedly sparse sculpt"
    assert receipt["source"]["mesh_count"]==1
    assert receipt["source_baseline_untouched"] is True
    return {"status":"CURVED_NONCANONICAL_GLTF_GEOMETRY_PASS",
            "triangles":total,"material_sections":len(mesh["primitives"]),
            "named_parts":len(parts),"sha256":receipt["source"]["sha256"]}

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: verify_ender_fidelity_v1.py <immutable pilot directory>")
    directory=Path(sys.argv[1])
    receipt=json.loads((directory/"receipt.json").read_text(encoding="utf-8"))
    print(json.dumps(check(directory/receipt["source"]["file"],receipt),indent=2))
