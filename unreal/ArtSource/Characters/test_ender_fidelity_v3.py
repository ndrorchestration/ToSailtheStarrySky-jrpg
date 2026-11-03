"""Regression tests for Ender V3 immutable static head-landmark candidate."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from build_ender_fidelity_v3 import build, BASELINES
from verify_ender_fidelity_v3 import verify

ROOT=Path(__file__).resolve().parent
CAND=ROOT/"FidelityCandidates"/"EnderV3"

class EnderV3Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out=Path(self.temp.name)/"v3"

    def test_checked_in_asset_and_predecessor_integrity(self):
        info=verify(CAND)
        self.assertEqual(info["status"],"V3_SOURCE_GEOMETRY_PASS_ART_HOLD")
        self.assertFalse(info["approval"])
        for p,sha in BASELINES.items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),sha)

    def test_generated_candidate_not_approved(self):
        r=build(self.out)
        proof=verify(self.out)
        self.assertEqual(proof["sha256"],r["source"]["sha256"])
        self.assertFalse(r["creator_approval"])
        self.assertFalse(r["skin_or_rigged"])
        self.assertIn("NOT RESOLVED",r["hair_color_state"])
        self.assertFalse(r["reference_space_measured_from_approved_image"])

    def test_deterministic_local_regeneration(self):
        a=build(self.out)
        b=build(Path(self.temp.name)/"v3again")
        self.assertEqual(a["source"]["sha256"],b["source"]["sha256"])

    def test_no_overwrite_predecessors_or_candidate(self):
        build(self.out)
        with self.assertRaises(FileExistsError):
            build(self.out)

    def test_tamper_rejected(self):
        r=build(self.out)
        p=self.out/r["source"]["file"]
        content=bytearray(p.read_bytes())
        content[-9]^=0x13
        p.write_bytes(content)
        with self.assertRaises(AssertionError):
            verify(self.out)

    def test_art_approval_or_landmark_forgery_rejected(self):
        build(self.out)
        p=self.out/"receipt.json"
        data=json.loads(p.read_text())
        data["creator_approval"]=True
        p.write_text(json.dumps(data))
        with self.assertRaises(AssertionError):
            verify(self.out)
        data["creator_approval"]=False
        data["reference_space_measured_from_approved_image"]=True
        p.write_text(json.dumps(data))
        with self.assertRaises(AssertionError):
            verify(self.out)

if __name__=="__main__":
    unittest.main()
