"""Engine-free QA for noncanonical Aureate Wake two-GLB lookdev source.

GLB generation and meter-scale checks run on Linux CI, NOT Unreal Editor.
"""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS=Path(__file__).resolve().parents[1]/"Tools"
sys.path.insert(0,str(TOOLS))
import author_aureate_body_pair as body


def glb_document(blob):
    if blob[:4]!=b"glTF" or len(blob)<28:
        raise AssertionError("Invalid GLB magic")
    version,total=struct.unpack_from("<II",blob,4)
    if version!=2 or total!=len(blob):
        raise AssertionError("Invalid GLB version or length")
    json_len,json_type=struct.unpack_from("<I4s",blob,12)
    if json_type!=b"JSON" or json_len%4:
        raise AssertionError("Invalid GLB JSON chunk")
    bin_start=20+json_len
    bin_len,bin_type=struct.unpack_from("<I4s",blob,bin_start)
    if bin_type!=b"BIN\x00" or bin_start+8+bin_len!=len(blob):
        raise AssertionError("Invalid GLB binary chunk")
    return json.loads(blob[20:bin_start].decode("utf-8"))


class BodyPairSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pair,cls.receipt=body.make_pair()
        cls.docs={name:glb_document(data) for name,data in cls.pair.items()}

    def test_provenance_and_two_distinct_review_only_assets(self):
        self.assertEqual(set(self.pair),{body.HULL,body.BRIDGE})
        self.assertEqual(self.receipt["status"],body.STATUS)
        self.assertEqual(self.receipt["approved_reference_sha256"],
            "03e3d500d8998a1377502f5ea28da79cf3eaf3854ece833d7ac25b4e0b268e13")
        self.assertEqual(set(self.receipt["destinations"]),set(self.pair))
        for name,blob in self.pair.items():
            self.assertEqual(hashlib.sha256(blob).hexdigest(),self.receipt["sha256"][name])
            self.assertTrue(self.docs[name]["extras"]["noGameplayOrCollision"])
            self.assertEqual(self.docs[name]["extras"]["orbiter"],"locked")

    def test_exact_meter_scale_and_single_mesh_three_materials(self):
        for name,doc in self.docs.items():
            self.assertEqual(doc["extras"]["sourceToGltfScale"],0.01)
            self.assertEqual(doc["extras"]["sourceUnits"],"centimeters")
            self.assertEqual(doc["extras"]["gltfLinearUnits"],"meters")
            self.assertEqual(len(doc["meshes"]),1)
            self.assertEqual(len(doc["materials"]),3)
            self.assertEqual(len(doc["meshes"][0]["primitives"]),3)
            self.assertTrue(all(p["mode"]==4 for p in doc["meshes"][0]["primitives"]))
            for p in doc["meshes"][0]["primitives"]:
                self.assertEqual(set(p["attributes"]),{"POSITION","NORMAL","TEXCOORD_0"})

    def test_hull_over_ten_meters_with_open_forward_deck(self):
        d=self.docs[body.HULL]
        positions=d["accessors"][d["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        self.assertAlmostEqual(positions["min"][0],-4.8,places=4)
        self.assertAlmostEqual(positions["max"][0],5.6,places=4)
        self.assertEqual([m["name"] for m in d["materials"]],
            ["M_WhitePearl_Hull_REVIEW","M_GoldSheerlines_REVIEW","M_AzureForedeck_REVIEW"])

    def test_bridge_panorama_has_translucent_review_glass(self):
        d=self.docs[body.BRIDGE]
        self.assertEqual(d["materials"][0]["alphaMode"],"BLEND")
        self.assertLess(d["materials"][0]["pbrMetallicRoughness"]["baseColorFactor"][3],0.5)
        self.assertTrue(any("Geodesic" in m["name"] for m in d["materials"]))
        positions=d["accessors"][d["meshes"][0]["primitives"][0]["attributes"]["POSITION"]]
        # GLB +Y is Unreal +Z. Body is ~1.48m tall plus a small cage.
        self.assertGreater(positions["max"][1],1.46)
        self.assertLess(positions["max"][1],1.49)

    def test_deterministic_output(self):
        pair2,receipt2=body.make_pair()
        self.assertEqual(self.pair,pair2)
        self.assertEqual(self.receipt,receipt2)

    def test_cli_rejects_overwriting_any_existing_review_folder(self):
        with tempfile.TemporaryDirectory() as d:
            folder=Path(d)/"review"
            folder.mkdir()
            (folder/"existing.txt").write_text("preserve")
            argv=["--output-dir",str(folder)]
            with self.assertRaises(SystemExit) as cm:
                body.main(argv)
            self.assertEqual(cm.exception.code,1)
            self.assertEqual((folder/"existing.txt").read_text(),"preserve")
            self.assertEqual(sorted(p.name for p in folder.iterdir()),["existing.txt"])


if __name__=="__main__":
    unittest.main()
