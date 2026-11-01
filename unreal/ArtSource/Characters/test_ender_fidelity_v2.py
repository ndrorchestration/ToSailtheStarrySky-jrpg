"""Engine-free regression and provenance tests for Ender V2 review asset."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from build_ender_fidelity_v2 import build
from verify_ender_fidelity_v2 import verify

ROOT=Path(__file__).resolve().parent
CAND=ROOT/"FidelityCandidates"/"EnderV2"
V1_SHA="3fc37924bb457dfe3b62877ca8709efb693a1c1c73251cf6f5dcfbe012babd38"
ORIGINAL_SHA="d516f68b49301cd04ae17c58eeeb2ca318b5f9b6a42f300be773fb62a7a3d6f2"
V2_SHA="e36f2f1daedbeefa53c54b92732e6b3498e4ea176c6f74f9f101e935a6b42bf8"

class EnderV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a=Path(self.tmp.name)/"one"

    def test_pinned_candidate_source_and_canon(self):
        p=verify(CAND)
        self.assertEqual(p["sha256"],V2_SHA)
        self.assertFalse(p["approval"])
        self.assertEqual(hashlib.sha256((ROOT/"Candidates"/"Ender.glb").read_bytes()).hexdigest(),ORIGINAL_SHA)
        self.assertEqual(hashlib.sha256((ROOT/"FidelityCandidates"/"EnderV1"/"Ender_ender_face_hair_v1.glb").read_bytes()).hexdigest(),V1_SHA)

    def test_generated_geometry_and_explicit_holds(self):
        r=build(self.a)
        p=verify(self.a)
        self.assertGreaterEqual(p["named_parts"],165)
        self.assertFalse(r["art_approval"])
        self.assertFalse(r["gameplay_ready"])
        self.assertIn("NOT RESOLVED",r["hair_color_state"])

    def test_same_host_byte_determinism(self):
        a=build(self.a)
        b=build(Path(self.tmp.name)/"two")
        self.assertEqual(a["source"]["sha256"],b["source"]["sha256"])

    def test_atomic_no_overwrite(self):
        build(self.a)
        with self.assertRaises(FileExistsError):
            build(self.a)

    def test_tamper_rejected(self):
        r=build(self.a)
        blob=self.a/r["source"]["file"]
        data=bytearray(blob.read_bytes());data[-5]^=0x10;blob.write_bytes(data)
        with self.assertRaises(AssertionError):
            verify(self.a)

    def test_checked_in_canonical_glb_fingerprint(self):
        d=json.loads((CAND/"receipt.json").read_text())
        self.assertEqual(d["source"]["sha256"],V2_SHA)
        self.assertEqual(hashlib.sha256((CAND/d["source"]["file"]).read_bytes()).hexdigest(),V2_SHA)

if __name__=="__main__":
    unittest.main()
