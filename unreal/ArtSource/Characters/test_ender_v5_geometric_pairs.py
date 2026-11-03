"""Negative controls: symmetry topology cannot establish face identity or approval."""
import copy
import json
import unittest

from verify_ender_v5_geometric_pairs import (
    SOURCE, REPORT, read_source, derive, verify_report
)

class V5GeometricPairSafety(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.native = read_source()
        cls.verified = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_native_report_matches_exact_bytes_and_pairing(self):
        report = verify_report(self.native, self.verified)
        self.assertEqual((report["negative_x_count"],report["positive_x_count"],
                          report["near_centerline_count"]),(32,32,15))
        self.assertEqual(len(report["mirror_pairs"]),32)
        self.assertEqual(report["source_landmark_count"],79)
        self.assertLessEqual(report["observed_max_pair_residual_cm"],0.15)
        self.assertEqual(report["status"],
                         "TECHNICAL_PAIRING_VERIFIED_SEMANTIC_MAPPING_HOLD")

    def test_no_anatomical_semantics_or_canon_claim(self):
        for key in ("point_indices_anatomically_labeled",
                    "image_space_coordinates_registered",
                    "approved_source_face_correspondence_established",
                    "secondary_shipdeck_used_for_face_landmarks",
                    "hair_conflict_resolved","face_sculpted",
                    "artist_likeness_approved","canonical_art_promoted"):
            self.assertFalse(self.verified[key])
            bad=copy.deepcopy(self.verified)
            bad[key]=True
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify_report(self.native,bad)

    def test_nonfinite_and_duplicate_indices_rejected(self):
        p=copy.deepcopy(self.native)
        p["points"][10]["xyz_cm"][1]=float("nan")
        with self.assertRaises(ValueError):
            derive(p)
        p=copy.deepcopy(self.native)
        p["points"][10]["index"]=9
        with self.assertRaises(ValueError):
            derive(p)

    def test_perturbed_pair_rejected(self):
        p=copy.deepcopy(self.native)
        p["points"][30]["xyz_cm"][2]+=1.0
        with self.assertRaises(ValueError):
            derive(p)

    def test_pair_and_centerline_tampering_rejected(self):
        for key in ("mirror_pairs","near_centerline_indices"):
            p=copy.deepcopy(self.verified)
            p[key]=[]
            with self.subTest(key=key),self.assertRaises(ValueError):
                verify_report(self.native,p)

    def test_native_byte_hash_guard(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as folder:
            from pathlib import Path
            path=Path(folder)/"altered.json"
            path.write_bytes(SOURCE.read_bytes()+b" ")
            with self.assertRaisesRegex(ValueError,"hash changed"):
                read_source(path)

if __name__=="__main__":
    unittest.main()
