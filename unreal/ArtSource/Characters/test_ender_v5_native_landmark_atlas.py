"""Regression and anti-likeness controls for read-only Ender V5 landmark atlas."""
import csv
import copy
import hashlib
import json
import struct
import unittest
from pathlib import Path

from verify_ender_v5_native_landmark_atlas import check_payload, STATUS
from verify_render_pngs import inspect_png

HERE=Path(__file__).resolve().parent
DATA=HERE/"ReviewEvidence"/"2026-11-02"/"EnderV5LandmarkAtlas"
NATIVE=DATA/"native_landmark_index.json"
ART=DATA/"TechnicalAtlas"

class LandmarkAtlasSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=json.loads(NATIVE.read_text(encoding="utf-8"))

    def test_native_index_snapshot_valid_only_not_likeness(self):
        result=check_payload(self.source)
        self.assertEqual(result["points"],79)
        self.assertFalse(result["approved_likeness"])
        self.assertGreater(result["x_span_cm"],10)
        self.assertGreater(result["z_span_cm"],10)

    def test_out_of_order_and_duplicate_index_fail(self):
        d=copy.deepcopy(self.source)
        d["points"][19]["index"]=18
        with self.assertRaisesRegex(ValueError,"Index"):
            check_payload(d)
        d=copy.deepcopy(self.source)
        d["points"]=list(reversed(d["points"]))
        with self.assertRaisesRegex(ValueError,"Index"):
            check_payload(d)

    def test_forged_image_approval_and_sculpt_state_fail(self):
        for k in ("likeness_approved","semantic_point_names_known",
                  "source_image_landmark_correspondences_approved",
                  "image_space_coordinates_measured","face_landmarks_edited",
                  "render_verified","rigged","skin_editing_available"):
            d=copy.deepcopy(self.source)
            d[k]=True
            with self.subTest(field=k),self.assertRaisesRegex(ValueError,"False promotion"):
                check_payload(d)

    def test_tampered_bounds_and_invalid_coords_fail(self):
        d=copy.deepcopy(self.source)
        min(d["points"],key=lambda entry:entry["xyz_cm"][0])["xyz_cm"][0]-=1
        with self.assertRaisesRegex(ValueError,"bounds"):
            check_payload(d)
        d=copy.deepcopy(self.source)
        d["points"][2]["xyz_cm"][1]=float("nan")
        with self.assertRaisesRegex(ValueError,"Nonfinite"):
            check_payload(d)

    def test_committed_technical_png_and_unmapped_csv_integrity(self):
        m=json.loads((ART/"atlas_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(m["point_count"],79)
        self.assertFalse(m["artist_reference_image_included"])
        self.assertFalse(m["owner_likeness_approved"])
        self.assertFalse(m["real_unreal_render"])
        for path,hash_field in ((NATIVE,"native_data_sha256"),
                                (ART/"v5_native_79_index_atlas.png","png_sha256"),
                                (ART/"v5_landmark_index_unmapped.csv","csv_sha256")):
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),m[hash_field])
        img=ART/"v5_native_79_index_atlas.png"
        self.assertEqual(inspect_png(img,(2560,1450))["sha256"],m["png_sha256"])
        with (ART/"v5_landmark_index_unmapped.csv").open(newline="",encoding="utf-8") as f:
            rows=list(csv.DictReader(f))
        self.assertEqual([int(row["native_index"]) for row in rows],list(range(79)))
        self.assertTrue(all(row["status"]=="UNMAPPED_REQUIRES_HUMAN_REVIEW"
                            and not row["human_reviewed_semantic_name"]
                            and not row["image_pixel_x"]
                            and not row["image_pixel_y"] for row in rows))

    def test_no_mutation_or_auto_approval_in_native_probe(self):
        script=(HERE/"capture_ender_v5_native_landmarks.py").read_text(encoding="utf-8")
        self.assertIn("Refuse overwrite",script)
        self.assertIn('face_landmarks_edited":False',script)
        self.assertIn("MH2",script)
        for dangerous in ("translate_face_landmarks(", "commit_face_state(",
                          "request_auto_rigging(", "save_asset(", "run_assembly("):
            self.assertNotIn(dangerous,script)

if __name__=="__main__":
    unittest.main()
