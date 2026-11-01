"""Independent semantic-pose gate for original glTF cast candidates.

This proves only source-space landmark ordering (glTF +Y up and +Z face
forward). It does not prove Unreal imported orientation, likeness or rigging.
"""
import hashlib
import json
import math
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parent / "Candidates"
NAMES = ("Ender", "Ionia", "Lyra", "Reson", "Aepex")

def require(ok, why):
    if not ok:
        raise ValueError(why)

def center(coords):
    return tuple((min(v[i] for v in coords) + max(v[i] for v in coords)) * .5
                 for i in range(3))

def read_landmarks(path, expected_sha):
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected_sha, "stale source/hash: " + path.name)
    require(data[:4] == b"glTF", "GLB magic: " + path.name)
    jlen, jtype = struct.unpack_from("<I4s", data, 12)
    require(jtype == b"JSON", "JSON chunk: " + path.name)
    doc = json.loads(data[20:20+jlen])
    binary_start = 28+jlen
    require(data[binary_start-4:binary_start] == b"BIN\x00", "BIN chunk: " + path.name)
    mesh = doc["meshes"][0]
    require(len(doc["meshes"]) == 1 and len(doc["nodes"]) == 1, "static-only source")
    # The generator exports one primitive per material. Part vertex offsets
    # are relative to that primitive, not relative to the full GLB.
    positions_by_material = {}
    for prim in mesh["primitives"]:
        acc = doc["accessors"][prim["attributes"]["POSITION"]]
        view = doc["bufferViews"][acc["bufferView"]]
        require(acc["type"] == "VEC3" and acc["componentType"] == 5126, "POSITION format")
        offset = binary_start + view.get("byteOffset",0) + acc.get("byteOffset",0)
        last = offset + acc["count"] * 12
        require(last <= len(data), "POSITION buffer range")
        pts = [struct.unpack_from("<3f", data, offset+i*12) for i in range(acc["count"])]
        require(all(math.isfinite(v) for p in pts for v in p), "finite POSITION")
        require(prim["material"] not in positions_by_material, "duplicate material primitive")
        positions_by_material[prim["material"]] = pts
    landmarks = {}
    for part in mesh["extras"]["partMap"]:
        points = positions_by_material[part["material"]]
        a = part["firstVertex"]; b = a + part["vertexCount"]
        require(0 <= a < b <= len(points), "part range: " + part["name"])
        require(part["name"] not in landmarks, "duplicate part name")
        landmarks[part["name"]] = center(points[a:b])
    return landmarks

def validate_pose(lm, name):
    required = ("Head sculpt", "Hair crown", "Torso shirt", "Pelvis",
                "L boot", "R boot", "L sclera", "R sclera", "Nose")
    require(all(k in lm for k in required), name+": missing named anatomy")
    head, hair, torso, pelvis = (lm[k] for k in required[:4])
    left_boot, right_boot = lm["L boot"], lm["R boot"]
    left_eye, right_eye, nose = lm["L sclera"], lm["R sclera"], lm["Nose"]
    require(hair[1] > head[1] > torso[1] > pelvis[1] >
            max(left_boot[1], right_boot[1]), name+": vertical landmark order")
    require(head[1]-max(left_boot[1],right_boot[1]) > 0.8, name+": head/foot separation")
    require(abs(head[0]) < .05 and left_boot[0] < -.035 and
            right_boot[0] > .035, name+": left/right boot orientation")
    require(left_eye[0] < -.01 and right_eye[0] > .01, name+": left/right eye orientation")
    require(nose[2] > head[2]+.07 and left_eye[2] > head[2]+.06 and
            right_eye[2] > head[2]+.06, name+": face should point +Z")
    return {"head_y_m":round(head[1],3),"boots_y_m":round((left_boot[1]+right_boot[1])/2,3),
            "face_forward":"+Z","up":"+Y"}

def negative_controls(lm):
    # The exact same landmarks rotated upside down must FAIL.
    inverted = {k:(v[0],-v[1],v[2]) for k,v in lm.items()}
    mirrored = {k:(-v[0],v[1],v[2]) for k,v in lm.items()}
    reversed_face = {k:(v[0],v[1],-v[2]) for k,v in lm.items()}
    for test, invalid in (("upside-down", inverted),("mirrored", mirrored),
                          ("backward-facing", reversed_face)):
        try:
            validate_pose(invalid, "NEGATIVE_"+test)
        except ValueError:
            print("CAST_POSE_NEGATIVE_REJECTED",test)
        else:
            raise AssertionError("negative control unexpectedly accepted: " + test)

def main():
    manifest = json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))
    records = manifest["characters"]
    require(tuple(r["name"] for r in records) == NAMES, "cast order")
    for r in records:
        lm = read_landmarks(ROOT/(r["name"]+".glb"), r["sha256"])
        result = validate_pose(lm, r["name"])
        print("CAST_SOURCE_POSE_PASS",r["name"],json.dumps(result,sort_keys=True))
        if r["name"] == "Ender":
            negative_controls(lm)

if __name__ == "__main__":
    main()

[executed on device: neontic (bcce7514-436c-4530-8f45-3b446e98a4b3)]