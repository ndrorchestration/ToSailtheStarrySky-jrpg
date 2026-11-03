"""Adversarial tests: a face-reference preference must not become sculpt approval."""
import copy
import json
import unittest

from verify_ender_v5_reference_priority import (
    POLICY_PATH, verify_reference_policy
)

class EnderV5ReferencePrioritySafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = json.loads(POLICY_PATH.read_text(encoding="utf-8"))

    def test_known_policy_passes_without_approval(self):
        result = verify_reference_policy(self.base)
        self.assertEqual(result["native_landmark_count"], 79)
        self.assertEqual(result["status"], "SOURCE_AUTHORITY_RECORDED_MAPPING_HOLD")

    def test_secondary_image_cannot_become_face_authority(self):
        for key, value in (
            ("creator_priority", "NEW_SHIPDECK_FACES"),
            ("secondary_shipdeck_usage", "FACE_LANDMARKS"),
            ("secondary_shipdeck_facial_landmarks_authorized", True),
            ("primary_source_selection", "SELECTED_AUTOMATICALLY"),
        ):
            p = copy.deepcopy(self.base)
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_reference_policy(p)

    def test_provisional_image_pixels_and_indices_cannot_be_published(self):
        for key, value in (
            ("image_x_px", 230), ("image_y_px", 105),
            ("native_index", 22), ("artist_verified", True)
        ):
            p = copy.deepcopy(self.base)
            p["proposal_points"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_reference_policy(p)

    def test_false_approval_and_hair_resolution_rejected(self):
        for key, value in (
            ("facial_sculpt_approved", True),
            ("canonical_face_asset_promoted", True),
            ("hair_color_conflict", "GREEN"),
            ("private_annotation_status", "APPROVED"),
            ("native_semantic_mapping_status", "VERIFIED"),
            ("image_space_coordinates_published", True),
            ("original_reference_image_copied_into_repository", True),
        ):
            p = copy.deepcopy(self.base)
            p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                verify_reference_policy(p)

    def test_wrong_reference_inventory_rejected(self):
        p = copy.deepcopy(self.base)
        p["earlier_face_reference_candidates"][0]["name"] = "New Ship Deck.webp"
        with self.assertRaisesRegex(ValueError, "reference inventory"):
            verify_reference_policy(p)

    def test_missing_or_reordered_feature_rejected(self):
        p = copy.deepcopy(self.base)
        p["proposal_points"][0], p["proposal_points"][1] = (
            p["proposal_points"][1], p["proposal_points"][0])
        with self.assertRaisesRegex(ValueError, "feature identity"):
            verify_reference_policy(p)

if __name__ == "__main__":
    unittest.main()
