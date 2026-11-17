"""Engine-free guard contracts for Ender Manny->Genesis9 retarget intake.

These tests verify that the native-only audit cannot mutate review assets or
infer finished animation from source filenames. They are not Unreal tests.
"""
from pathlib import Path
import ast
import re
import unittest


SOURCE = (Path(__file__).resolve().parent /
          "inspect_ender_manny_retarget_prereqs.py").read_text(encoding="utf8")


class EnderRetargetPrerequisiteContracts(unittest.TestCase):
    def test_native_audit_is_syntactically_valid(self):
        ast.parse(SOURCE)

    def test_all_three_distinct_locomotion_roles(self):
        self.assertIn('"idle": "/Game/Mannequins/Anims/Unarmed/MM_Idle"', SOURCE)
        self.assertIn('"walk": "/Game/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"', SOURCE)
        self.assertIn('"run_candidate": "/Game/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"', SOURCE)
        self.assertIn('SOURCE_TARGET_SKELETON_COLLISION', SOURCE)
        self.assertIn('CLIP_NOT_SOURCE_SKELETON_', SOURCE)
        self.assertIn('ROOT_MOTION_ENABLED_', SOURCE)

    def test_fingerprint_all_local_inputs_without_commit(self):
        hashes = re.findall(r'": "([a-f0-9]{64})"', SOURCE)
        self.assertGreaterEqual(len(hashes), 7)
        self.assertEqual(len(hashes), len(set(hashes)))
        for name in ("SKM_Manny_Simple.uasset", "SK_Mannequin.uasset",
                     "MM_Idle.uasset", "MF_Unarmed_Walk_Fwd.uasset",
                     "MF_Unarmed_Jog_Fwd.uasset",
                     "Genesis9_BaseShirtShorts_MergedRig_REVIEW_Skeleton.uasset"):
            self.assertIn(name, SOURCE)

    def test_requires_genuine_engine_bone_parent_checks(self):
        self.assertIn("get_bone_parent(src[1])", SOURCE)
        self.assertIn("get_bone_parent(tgt[1])", SOURCE)
        self.assertIn("BONE_CHAIN_NOT_PRESENT_", SOURCE)
        self.assertIn("IK_RIG_EDITOR_PLUGIN_MISSING", SOURCE)

    def test_does_not_create_or_bind_any_animation(self):
        for forbidden in ("create_asset(", "set_editor_property(",
                          "save_loaded_asset(", "duplicate_and_retarget(",
                          "run_batch_retarget(", "PlayAnimation(",
                          "play_animation(", "spawn_actor(", "open_level("):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, SOURCE)
        for hold in ('"retarget_performed": False',
                     '"animation_playback_verified": False',
                     '"foot_contact_verified": False',
                     '"creator_art_approved": False',
                     '"map_or_asset_saved": False'):
            self.assertIn(hold, SOURCE)

    def test_review_only_exact_local_project_and_version(self):
        self.assertIn("WRONG_PROJECT", SOURCE)
        self.assertIn("WRONG_ENGINE", SOURCE)
        self.assertIn("5.8.4-", SOURCE)
        self.assertIn("LOCAL_UASSET_HASH_MISMATCH_", SOURCE)
        self.assertIn('unreal.SystemLibrary.quit_editor()', SOURCE)


if __name__ == "__main__":
    unittest.main()
