"""Engine-free, dependency-free gates for original Ender V1/V2 lookdev hair GLBs."""
import hashlib
import json
import struct
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
VERSIONS={
    "V1": ("Candidates/Ender_DarkCopper_LayeredHair_V1_NONCANONICAL.glb",
           "01bb9f400454d633c5e887cd47a12fd1af34e5bbf6b7c05ab6a5929b0a6db562",43634),
    "V2": ("CandidatesV2/Ender_DarkCopper_LayeredHair_V2_NONCANONICAL.glb",
           "0da20d3b34e3fdf6171476db1736d2e2607987c71403272207e428f18c8ca9cd",28544)
}
MATERIALS=["DeepCopperRoots","WarmChestnutBase","TousledAuburnBody",
           "CopperRimHighlights","ShadowBrownStrands"]

def require(valid,msg):
    if not valid:raise AssertionError("FAIL_CLOSED "+msg)

def inspect(data,expected_sha,expected_triangles):
    require(hashlib.sha256(data).hexdigest()==expected_sha,"pinned source hash")
    require(len(data)>500_000 and data[:4]==b"glTF","genuine nonempty 3D GLB")
    version,total=struct.unpack_from("<II",data,4)
    require(version==2 and total==len(data),"GLB v2 exact byte size")
    n,kind=struct.unpack_from("<I4s",data,12)
    require(kind==b"JSON" and n%4==0 and 20+n+8<len(data),"JSON chunk")
    doc=json.loads(data[20:20+n])
    binlen,bintag=struct.unpack_from("<I4s",data,20+n)
    require(bintag==b"BIN\x00" and 28+n+binlen==len(data),"BIN exact length")
    require(doc["buffers"][0]["byteLength"]==binlen,"GLB buffer bounds")
    require(len(doc.get("meshes",[]))==1 and len(doc["meshes"][0]["primitives"])==5,
            "exact original static mesh")
    require(len(doc.get("materials",[]))==5 and
            [x["name"] for x in doc["materials"]]==MATERIALS,"palette lock")
    require(not doc.get("skins") and not doc.get("animations"),
            "no fake animation or rig")
    extras=doc.get("extras",{})
    for key in ("review_only","source_authored"):
        require(extras.get(key) is True,key+" required")
    for key in ("creator_approved","actual_head_fit_verified","gameplay_asset",
                "rigged","groom","source_reference_pixels_included"):
        require(extras.get(key) is False,key+" MUST remain false")
    triangles=0
    ids=set()
    for p in doc["meshes"][0]["primitives"]:
        require(p.get("mode")==4,"triangles")
        ids.add(p["material"])
        pos=doc["accessors"][p["attributes"]["POSITION"]]
        norm=doc["accessors"][p["attributes"]["NORMAL"]]
        indices=doc["accessors"][p["indices"]]
        require(pos["count"]==norm["count"] and pos["type"]=="VEC3",
                "position/normal count")
        require(norm["type"]=="VEC3" and indices["type"]=="SCALAR","shape")
        require(indices["count"]%3==0,"triangle indices")
        triangles += indices["count"]//3
        for accession in (pos,norm,indices):
            buf=doc["bufferViews"][accession["bufferView"]]
            require(buf["buffer"]==0 and buf["byteOffset"]+buf["byteLength"]<=binlen,
                    "accessor bounds")
    require(ids==set(range(5)),"5 unique material IDs")
    require(triangles==expected_triangles,"triangle-budget custody")
    return doc

class ReviewHairSourceTests(unittest.TestCase):
    def test_v1_exact_source(self):
        name,sha,tri=VERSIONS["V1"]
        inspect((HERE/name).read_bytes(),sha,tri)
    def test_v2_exact_source(self):
        name,sha,tri=VERSIONS["V2"]
        inspect((HERE/name).read_bytes(),sha,tri)
    def test_v1_v2_are_distinct_review_assets(self):
        self.assertNotEqual(VERSIONS["V1"][1],VERSIONS["V2"][1])
        self.assertGreater(VERSIONS["V1"][2],VERSIONS["V2"][2])
    def test_reject_binary_tamper(self):
        name,sha,tri=VERSIONS["V2"]
        data=(HERE/name).read_bytes()
        bad=bytearray(data);bad[-30] ^= 1
        with self.assertRaises(AssertionError):inspect(bytes(bad),sha,tri)
    def test_reject_forged_approved_source_even_without_hash_requirement(self):
        name,sha,tri=VERSIONS["V2"]
        data=(HERE/name).read_bytes()
        self.assertIn(b'"creator_approved":false',data)
        bad=data.replace(b'"creator_approved":false',
                         b'"creator_approved":true ',1)
        bad_hash=hashlib.sha256(bad).hexdigest()
        with self.assertRaises(AssertionError):
            inspect(bad,bad_hash,tri)
    def test_no_production_rename_or_native_promotion_source(self):
        for filename in (
            "native_import_ender_hair_v1_20261104.py",
            "native_import_ender_hair_v2_20261104.py",
            "native_capture_ender_hair_v1_v2_goggles_20261104.py",
            "native_capture_ender_hair_v2_v2_goggles_20261104.py",
            "native_probe_v5_head_bounds_20261104.py"):
            script=(HERE/filename).read_text(encoding="utf-8")
            self.assertIn("c:/mh5/castallsandbox",script)
            self.assertNotIn("save_current_level(",script)
            self.assertNotIn("source_assets_saved=True",script)

if __name__=="__main__":
    unittest.main()
