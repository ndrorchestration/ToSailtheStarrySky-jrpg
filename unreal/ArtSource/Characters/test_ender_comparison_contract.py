"""Engine-free negative controls for disposable Unreal comparison stage."""
import copy
import tempfile
from pathlib import Path
import json
import unittest
import ender_comparison_contract as contract


def example(name):
    return {
        "status": "NATIVE_IMPORT_PASS_ART_UNAPPROVED",
        "source_sha256": contract.EXPECTED[name]["sha256"],
        "asset": contract.EXPECTED[name]["asset_fragment"] + "Mesh.Mesh",
        "visual_acceptance": False,
        "creator_approval": False,
        "skin_or_rigged": False,
        "baseline_cast_unchanged": True,
    }


class ComparisonContractTests(unittest.TestCase):
    def test_native_review_plan_and_height_canon(self):
        plan = contract.review_plan()
        self.assertFalse(plan["end_user_visual_approval"])
        self.assertTrue(plan["source_character_models_unchanged"])
        self.assertEqual(plan["height_order_canon"], "Reson > Aepex > Ender > Ionia > Lyra")
        self.assertEqual(len(plan["cameras"]), 2)
        self.assertEqual(plan["camera_projections"]["comparison_three_quarter"]["ortho_width_cm"], 480.0)

    def test_disposable_project_only(self):
        with self.assertRaisesRegex(ValueError, "non-disposable"):
            contract.check_project("/Game/ToSailTheStarrySky")
        self.assertEqual(contract.check_project("/tmp/CastAllSandbox").name, "CastAllSandbox")

    def test_native_sha_and_asset_lock(self):
        for name in contract.EXPECTED:
            self.assertIn("/Game/ArtLookdev/", contract.validate_native_intake(name, example(name)))
            for bad_field, bad_value in [
                ("source_sha256", "0" * 64), ("visual_acceptance", True),
                ("creator_approval", True), ("skin_or_rigged", True),
                ("baseline_cast_unchanged", False),
                ("asset", "/Game/Characters/Ender.M1"), ("status", "UNVERIFIED")]:
                bad = example(name)
                bad[bad_field] = bad_value
                with self.assertRaises(ValueError, msg=f"{name} {bad_field}"):
                    contract.validate_native_intake(name, bad)

    def test_required_receipts_or_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "CastAllSandbox"
            path = project / "Saved" / "CharacterLookdev"
            path.mkdir(parents=True)
            for name, data in contract.EXPECTED.items():
                (path / data["receipt"]).write_text(json.dumps(example(name)), encoding="utf-8")
            self.assertEqual(len(contract.load_intake_receipts(project)), 2)
            (path / contract.EXPECTED["EnderV2"]["receipt"]).unlink()
            with self.assertRaises(FileNotFoundError):
                contract.load_intake_receipts(project)

    def test_camera_and_layout_negative_controls(self):
        old = contract.CANDIDATE_POSITIONS
        try:
            contract.CANDIDATE_POSITIONS = {"EnderV1": (-115, 0, 0), "EnderV2": (115, 20, 0)}
            with self.assertRaisesRegex(ValueError, "depth matched"):
                contract.review_plan()
        finally:
            contract.CANDIDATE_POSITIONS = old
        oldcam = contract.CAMERAS
        try:
            contract.CAMERAS = (("comparison_front", (0, -590, 108), 90, 43), oldcam[1])
            with self.assertRaisesRegex(ValueError, "face source-native"):
                contract.review_plan()
        finally:
            contract.CAMERAS = oldcam


if __name__ == "__main__":
    unittest.main()
