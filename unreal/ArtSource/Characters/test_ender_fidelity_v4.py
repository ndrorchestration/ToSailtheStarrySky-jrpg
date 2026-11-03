"""Immutable Ender V4 source/geometry and authority-negative tests."""
import hashlib
import json
import tempfile
from pathlib import Path
import unittest
from build_ender_fidelity_v4 import build,PREDECESSOR_HASHES,ROOT,assemble_v3,retopology_study_face,replace_facial_features
from verify_ender_fidelity_v4 import verify

PINNED=ROOT/"FidelityCandidates"/"EnderV4"

class V4SourceTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.a=Path(self.tmp.name)/"one"

    def test_pinned_glb_and_all_predecessors(self):
        p=verify(PINNED)
        self.assertEqual(p["status"],"V4_GLTF_TOPOLOGY_PASS_CINEMATIC_LIKENESS_HOLD")
        for name,sha in PREDECESSOR_HASHES.items():
            self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),sha)

    def test_fresh_candidate_is_unrigged_review_only(self):
        receipt=build(self.a)
        p=verify(self.a)
        self.assertEqual(p["sha256"],receipt["source"]["sha256"])
        self.assertFalse(receipt["author_approved_likeness"])
        self.assertFalse(receipt["reference_space_measured_from_approved_image"])
        self.assertIn("HOLD",receipt["unresolved_hair_color"])

    def test_host_determinism_and_atomic_refusal(self):
        a=build(self.a)
        b=build(Path(self.tmp.name)/"two")
        self.assertEqual(a["source"]["sha256"],b["source"]["sha256"])
        with self.assertRaises(FileExistsError):
            build(self.a)

    def test_tamper_and_false_approval_rejected(self):
        r=build(self.a)
        blob=self.a/r["source"]["file"]
        changed=bytearray(blob.read_bytes());changed[-3]^=1;blob.write_bytes(changed)
        with self.assertRaises(AssertionError):
            verify(self.a)
        # Reset only fresh temporary source and falsify approval state.
        blob.write_bytes((PINNED/r["source"]["file"]).read_bytes())
        rec=self.a/"receipt.json"
        d=json.loads(rec.read_text(encoding="utf-8"))
        d["author_approved_likeness"]=True
        rec.write_text(json.dumps(d),encoding="utf-8")
        with self.assertRaises(AssertionError):
            verify(self.a)

    def test_eye_elements_recessed_after_first_native_visual_defect(self):
        b=assemble_v3()
        retopology_study_face(b)
        replace_facial_features(b)
        for side in ("L","R"):
            eye=[p for p in b.parts if p[0]=="V4 "+side+" shallow eye almond"]
            self.assertEqual(len(eye),1)
            center_z=sum(v[2] for v in eye[0][1])/len(eye[0][1])
            # The first UE V4 frame revealed prominent disconnected eyeballs
            # at z=.111; V4 eye-fit trial moves them closer to the orbital face.
            self.assertLess(center_z,.102)
            self.assertGreater(center_z,.09)

    def test_reference_false_claim_rejected(self):
        build(self.a)
        p=self.a/"receipt.json"
        r=json.loads(p.read_text(encoding="utf-8"))
        r["reference_space_measured_from_approved_image"]=True
        p.write_text(json.dumps(r),encoding="utf-8")
        with self.assertRaises(AssertionError):
            verify(self.a)

if __name__=="__main__":
    unittest.main()
