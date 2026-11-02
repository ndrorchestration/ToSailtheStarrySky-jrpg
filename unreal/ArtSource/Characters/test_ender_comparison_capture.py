"""Fail-closed native PNG provenance QA tests without Unreal installation."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from ender_comparison_contract import EXPECTED, CAMERAS, CAMERA_PROJECTIONS, MAP
import verify_ender_comparison_report as subject


def receipt():
    return {
        "status": "UNREAL_SCREENSHOT_TASKS_COMPLETE_NATIVE_PNG_QA_PENDING",
        "map": MAP,
        "camera_projections": CAMERA_PROJECTIONS,
        "engine": "5.8.4-58902052+++UE5+Release-5.8",
        "saved_review_map_sha256_before": "a" * 64,
        "saved_review_map_sha256_after": "a" * 64,
        "source_sha256": {key: info["sha256"] for key, info in EXPECTED.items()},
        "reference_likeness_approved": False,
        "source_files_modified": False,
        "saved_unreal_map_modified": False,
        "capture_tasks": [{"name": row[0], "requested": "C:/review/" + row[0] + ".png", "ticks": 9} for row in CAMERAS],
    }


class NativeComparisonReceiptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "receipt.json"

    def call(self, content, png_hashes=("sha-a", "sha-b")):
        self.path.write_text(json.dumps(content), encoding="utf-8")
        with patch.object(subject, "resolve_capture", side_effect=lambda folder, name: self.root / (name + ".png")), \
             patch.object(subject, "inspect_png", side_effect=[{"sha256": x} for x in png_hashes]), \
             patch.object(subject, "check_pair_coverage", return_value={"regions": {"left": 0.12, "right": 0.11}}), \
             patch.object(subject, "check_pair_apparent_height", return_value={"height_ratio": 1.01}):
            return subject.verify(self.root, self.path)

    def test_complete_real_distinct_pngs_required(self):
        result = self.call(receipt())
        self.assertEqual(result["status"], "NATIVE_COMPARISON_IMAGE_INTEGRITY_PASS_NOT_ART_ACCEPTANCE")
        self.assertFalse(result["owner_approved"])
        self.assertEqual(len(result["images"]), 2)

    def test_duplicate_images_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicated"):
            self.call(receipt(), ("same", "same"))

    def test_false_source_canon_or_camera_evidence_rejected(self):
        fields = [
            ("status", "PENDING"), ("map", "other"),
            ("camera_projections", {"comparison_front": {"mode": "perspective"}}),
            ("reference_likeness_approved", True),
            ("source_files_modified", True), ("saved_unreal_map_modified", True),
            ("capture_tasks", [{"name": "comparison_front"}]),
            ("source_sha256", {"EnderV1": "0" * 64}),
            ("engine", "5.7.0"),
            ("saved_review_map_sha256_before", "a" * 63),
            ("saved_review_map_sha256_after", "b" * 64),
            ("capture_tasks", [
                {"name": row[0], "requested": "C:/wrong.png", "ticks": 9} for row in CAMERAS]),
        ]
        for field, bad in fields:
            item = receipt()
            item[field] = bad
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.call(item)


if __name__ == "__main__":
    unittest.main()
