"""No-engine QA for Aureate Wake V2: preserve V1 proof, reject art promotion."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

ART=Path(__file__).resolve().parents[1]/"ArtSource"/"ShipReview"
sys.path.insert(0,str(ART))
import build_aureate_body_review as v1
import build_aureate_fidelity_v2 as v2

ORIGINAL_V1_HASHES={
    "AureateWake_Hull_Lookdev.glb":"a549c6737d59416645f1ead0a9d6531f6f314ba6bb774cbdd56b19b65a03ba22",
    "AureateWake_BridgeDome_Lookdev.glb":"c2043ae7eaf94d4fa2aa42bfbd5e147918bc4344b21e3798b7d9bc4b726224f3",
}


def doc(blob:bytes)->dict:
    if len(blob)<32 or blob[:4]!=b"glTF": raise AssertionError("GLB header")
    version,total=struct.unpack_from("<II",blob,4)
    if version!=2 or total!=len(blob):raise AssertionError("GLB size")
    length,kind=struct.unpack_from("<I4s",blob,12)
    if kind!=b"JSON" or length%4:raise AssertionError("JSON alignment")
    bsize,btype=struct.unpack_from("<I4s",blob,20+length)
    if btype!=b"BIN\0" or bsize%4 or 28+length+bsize!=len(blob):
        raise AssertionError("GLB BIN chunk")
    return json.loads(blob[20:20+length])


class ApprovedDirectionV2Tests(unittest.TestCase):
    def test_original_exact_sha_unchanged(self):
        original=v1.build_payloads()
        self.assertEqual({n:hashlib.sha256(x).hexdigest() for n,x in original.items()},
                         ORIGINAL_V1_HASHES)

    def test_palette_v2_does_not_mutate_original(self):
        before=v1.build_payloads()
        _=v2.deterministic_payloads()
        self.assertEqual(before,v1.build_payloads())

    def test_reproducible_two_named_glbs(self):
        a=v2.deterministic_payloads()
        self.assertEqual(a,v2.deterministic_payloads())
        self.assertEqual(set(a),set(v2.FILES))
        self.assertTrue(all(25000<len(blob)<1500000 for blob in a.values()))

    def test_material_color_and_glass_transparency(self):
        out=v2.deterministic_payloads()
        for name,blob in out.items():
            d=doc(blob)
            self.assertEqual(len(d["meshes"]),1)
            self.assertEqual(len(d["meshes"][0]["primitives"]),3)
            self.assertEqual(len(d["materials"]),3)
            self.assertEqual(d["extras"]["authority"],v1.STATUS)
            self.assertEqual(d["extras"]["sourceToGltfScale"],.01)
            for idx,mat in enumerate(d["materials"]):
                self.assertEqual(d["meshes"][0]["primitives"][idx]["material"],idx)
                self.assertTrue(mat["name"].endswith("APPROVAL_STUDY"))
            if name==v2.FILES[0]:
                ivory=d["materials"][0]["pbrMetallicRoughness"]["baseColorFactor"]
                navy=d["materials"][2]["pbrMetallicRoughness"]["baseColorFactor"]
                self.assertGreater(ivory[0],.85)
                self.assertGreater(ivory[1],.8)
                self.assertLess(navy[0],.08)
                self.assertLess(navy[2],.22)
            else:
                glass=d["materials"][0]
                self.assertEqual(glass["alphaMode"],"BLEND")
                self.assertLess(glass["pbrMetallicRoughness"]["baseColorFactor"][3],.4)

    def test_meter_scale_envelopes_and_three_sections(self):
        for name,blob in v2.deterministic_payloads().items():
            d=doc(blob)
            mins=[];maxs=[]
            for primitive in d["meshes"][0]["primitives"]:
                acc=d["accessors"][primitive["attributes"]["POSITION"]]
                self.assertEqual(acc["type"],"VEC3")
                self.assertGreater(acc["count"],20)
                mins.append(acc["min"]);maxs.append(acc["max"])
                self.assertEqual(primitive["mode"],4)
            mi=[min(p[i] for p in mins) for i in range(3)]
            ma=[max(p[i] for p in maxs) for i in range(3)]
            if name==v2.FILES[0]:
                self.assertTrue(-4.05<mi[0]<-3.95)
                self.assertTrue(3.95<ma[0]<4.05)
                self.assertTrue(-.60<mi[1]<-.20)
                self.assertTrue(-1.3<mi[2]<-.70 and .70<ma[2]<1.3)
            else:
                self.assertTrue(-1.05<mi[0]<-.8 and .8<ma[0]<1.05)
                self.assertTrue(-.80<mi[1]<-.40 and .4<ma[1]<.80)

    def test_new_visual_details_have_greater_geometry(self):
        h0,h1=v1.hull(),v2.hull_v2()
        self.assertEqual(len(h0),len(h1))
        self.assertGreater(sum(len(s.indices) for s in h1),
                           sum(len(s.indices) for s in h0)+450)
        b0,b1=v1.bridge_dome(),v2.dome_v2()
        self.assertGreater(sum(len(s.indices) for s in b1),
                           sum(len(s.indices) for s in b0))

    def test_manifest_never_approves_art(self):
        m=v2.manifest(v2.deterministic_payloads())
        self.assertEqual(m["original_creator_approved_reference_sha256"],
                         v2.APPROVED_IMAGE_SHA256)
        self.assertEqual(m["status"],"NONCANONICAL_REVIEW_NOT_ART_ACCEPTED")
        self.assertEqual(m["creator_3d_art_approval"],"NOT_GRANTED")
        self.assertEqual(m["native_unreal_import"],"NOT_VERIFIED")
        self.assertFalse(m["orbiter_authorized"])
        self.assertFalse(m["gameplay_modified"])
        self.assertEqual(set(m["sha256"]),set(v2.FILES))

    def test_build_then_verify_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            v2.write_or_verify(folder,True)
            v2.write_or_verify(folder,False)
            self.assertEqual(len(list(folder.iterdir())),3)
            p=folder/v2.FILES[0]
            contents=p.read_bytes()
            p.write_bytes(contents[:-1]+bytes([contents[-1]^1]))
            with self.assertRaisesRegex(ValueError,"refuse|Refuse"):
                v2.write_or_verify(folder,True)
            with self.assertRaisesRegex(ValueError,"refuse|Refuse"):
                v2.write_or_verify(folder,False)

    def test_build_refuses_modified_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)
            v2.write_or_verify(folder,True)
            p=folder/v2.MANIFEST_NAME
            m=json.loads(p.read_text())
            m["orbiter_authorized"]=True
            p.write_text(json.dumps(m),encoding="utf-8")
            with self.assertRaises(ValueError):
                v2.write_or_verify(folder,False)

    def test_separate_v2_assets_cannot_auto_bind_to_production(self):
        source=(ART/"build_aureate_fidelity_v2.py").read_text(encoding="utf-8")
        self.assertNotIn("import unreal",source)
        self.assertNotIn("save_map(",source)
        self.assertNotIn("RequestForm(",source)
        self.assertNotIn("set_editor_property(",source)


if __name__=="__main__":
    unittest.main()
