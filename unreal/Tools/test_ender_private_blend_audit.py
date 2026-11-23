"""Guard private Ender asset audit and comparison guide against scope drift."""
import ast
import unittest
from pathlib import Path
BASE = Path(__file__).resolve().parent
AUDIT = (BASE / "audit_ender_private_blend_assets.py").read_text(encoding="utf8")
HOST = (BASE / "Invoke-EnderPrivateBlendAudit.ps1").read_text(encoding="utf8")
GUIDE = (BASE.parent / "Docs/ENDER_LOCOMOTION_REFERENCE_BENCHMARK_2026_11_23.md").read_text(encoding="utf8")


class EnderPrivateBlendAuditTests(unittest.TestCase):
    def test_native_script_is_parseable_and_read_only(self):
        ast.parse(AUDIT)
        for forbidden in (
            "EditorAssetLibrary.save_asset(",
            "AssetToolsHelpers.get_asset_tools().create_asset(",
            "ResampleData(",
            "try_create_connection(",
            "SetAnimInstanceClass(",
            "save_package(",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, AUDIT)

    def test_strict_identity_and_custody_guards(self):
        for required in (
            "TSTSS_ENDER_AUDIT_EXPECTED_HEAD",
            "TSTSS_ENDER_AUDIT_RECEIPT",
            "RECEIPT_OUTSIDE_EVIDENCE",
            "RECEIPT_NOT_NEW",
            "BLEND_SAMPLE_COUNT",
            "CLIP_SKELETON_MISMATCH",
            "ANIMBP_SKELETON",
            "POSE_OUTPUT",
            "SPEED_INPUT",
            "ROOT_MOTION_MODE",
            "PRIVATE_BINARY_NOT_IGNORED",
            "hashlib.sha256(",
        ):
            with self.subTest(required=required):
                self.assertIn(required, AUDIT)

    def test_only_explicit_private_character_paths(self):
        self.assertIn("EnderRetarget_NONCANONICAL", AUDIT)
        self.assertIn("BlendReview_PRIVATE", AUDIT)
        self.assertIn("ABP_EnderIdleWalkRun_V1_PRIVATE", AUDIT)
        self.assertIn("BS_EnderIdleWalkRun_V1_NONCANONICAL", AUDIT)
        for required in ("MM_Idle_EnderPreview_NONCANONICAL",
                         "MF_Unarmed_Walk_Fwd_EnderSpineFixV1_PRIVATE",
                         "MF_Unarmed_Jog_Fwd_EnderSpineFixV1_PRIVATE"):
            self.assertIn(required, AUDIT)

    def test_host_fails_closed_and_restores_only_known_unreal_config_drift(self):
        for required in (
            "HOLD_ENDER_PRIVATE_ASSET_AUDIT_",
            "ENGINE_BUSY",
            "WRONG_HEAD",
            "SOURCE_DIRTY",
            "Config/DefaultEngine.ini",
            "Config/DefaultInput.ini",
            "ENGINE_LEFT_RUNNING",
            "DIRTY_AFTER_AUDIT",
            "NATIVE_EXECUTION_FAILED",
            "EVIDENCE=",
        ):
            with self.subTest(required=required):
                self.assertIn(required, HOST)
        for forbidden in ("git -C $root reset --hard", "git -C $root clean -fd",
                          "git -C $root push", "git -C $root merge"):
            self.assertNotIn(forbidden, HOST)

    def test_comparison_is_not_commercial_animation_copy(self):
        for item in ("Final Fantasy VII Rebirth", "Tales of Arise",
                     "Game Animation Sample Project", "Lyra",
                     "260 cm/s", "600 cm/s",
                     "NOT a completed equivalence/ranking", "not verified planted-ground",
                     "side-by-side", "Do not"):
            self.assertIn(item.lower(), GUIDE.lower())
        self.assertIn("no merge, release", GUIDE.lower())


if __name__ == "__main__":
    unittest.main()
