"""Negative and source-contract verification for opt-in private animation export.

Passing these tests is NOT evidence of UE execution, in-place root movement,
correct gait, rendered footage, or an approved playable Ender.
"""
from pathlib import Path
import ast
import unittest

SCRIPT = (Path(__file__).resolve().parent /
          "retarget_private_ender_locomotion_candidates.py").read_text(encoding="utf8")


class PrivateAnimationCandidateContracts(unittest.TestCase):
    def test_python_valid(self):
        ast.parse(SCRIPT)

    def test_private_opt_in_and_native_host_authority(self):
        for gate in (
            'os.environ.get("TSTSS_PRIVATE_ANIM_RETARGET") == "1"',
            'gate.get("mode") == "retarget-clips"',
            'gate.get("source_head") == head',
            'gate.get("run_id") == os.environ.get("TSTSS_PRIVATE_IK_RUN_ID")',
            '"HOST_STARTUP_RESERVE"',
            '"RUNTIME_RAM"', '"RUNTIME_DISK"',
            'rig.get("status") ==',
            '"REOPENED_SOURCE_AND_TARGET_IK_AND_RTG_PASS_NO_ANIM"',
            '"AUDIT_NOT_CURRENT_OR_VALID"',
            '"AUDIT_STALE"',
        ):
            self.assertIn(gate, SCRIPT)

    def test_immutable_three_source_sequences_and_target_rig(self):
        for name in (
            "MM_Idle", "MF_Unarmed_Walk_Fwd", "MF_Unarmed_Jog_Fwd",
            "IK_Manny_EnderReview_NONCANONICAL",
            "IK_Genesis9_EnderReview_NONCANONICAL",
            "RTG_MannyToEnder_NONCANONICAL",
            "Genesis9_BaseShirtShorts_MergedRig_REVIEW",
        ):
            # The two IK names are deliberately checked via native receipt
            # hashes, rather than hardcoded in the batch script.
            if name.startswith("IK_"):
                continue
            self.assertIn(name, SCRIPT)
        self.assertIn("for name, digest in rig[\"sha256\"].items():", SCRIPT)
        self.assertIn("INPUT_SHA", SCRIPT)
        self.assertIn("SOURCE_ROOT_MOTION_FLAG_DRIFT", SCRIPT)
        self.assertIn("SOURCE_SKELETON_DRIFT", SCRIPT)
        self.assertIn("TARGET_SKELETON_DRIFT", SCRIPT)

    def test_zero_overwrite_and_no_source_asset_mutation(self):
        for rule in (
            'overwrite_existing_files=False',
            'include_referenced_assets=False',
            'use_source_path=False',
            '"REVIEW_OUTPUT_ALREADY_EXISTS_"',
            '"PRIVATE_OUTPUT_NOT_EXCLUDED"',
            '"OUTPUT_PACKAGE_ESCAPE"',
            '"OUTPUT_NAMES_NOT_EXACT"',
            "ik_retarget_asset=rtg",
            "run_batch_retarget(inputs)",
        ):
            self.assertIn(rule, SCRIPT)
        for forbidden in (
            "duplicate_and_retarget(", "delete_asset(",
            "SaveGameToSlot(", "save_current_level(",
            "set_actor_location(", "git push", "git add",
            "move_file(", "rename_asset(", "shutil.rmtree(",
        ):
            self.assertNotIn(forbidden, SCRIPT)

    def test_no_unverified_visual_or_root_motion_acceptance(self):
        self.assertIn('"source_root_motion_roles": ["walk", "run_candidate"]', SCRIPT)
        self.assertIn('"allow_direct_source_clip_assignment": False', SCRIPT)
        self.assertIn('"in_place_conversion_verified": False', SCRIPT)
        self.assertIn('"animation_pawn_assignment": False', SCRIPT)
        self.assertIn('"rendered_foot_contact_verified": False', SCRIPT)
        self.assertIn('"creator_art_approved": False', SCRIPT)
        self.assertIn('PRIVATE_RETARGET_CLIP_CANDIDATES_CREATED_NOT_PLAYBACK_ACCEPTED', SCRIPT)

    def test_negative_mutation_of_privacy_is_detectable(self):
        for gate in (
            'overwrite_existing_files=False',
            'not unreal.EditorAssetLibrary.does_asset_exist(OUTPUT + "/" + name)',
            'check.returncode == 0',
            'sha256(path) == expected',
            'data.is_valid()',
            'require(len(result) == 3',
            'require(skel and skel.get_path_name() == audit["target_skeleton"]',
        ):
            with self.subTest(gate=gate):
                self.assertIn(gate, SCRIPT)
                self.assertNotIn(gate, SCRIPT.replace(gate, "/* omitted */"))


if __name__ == "__main__":
    unittest.main()
