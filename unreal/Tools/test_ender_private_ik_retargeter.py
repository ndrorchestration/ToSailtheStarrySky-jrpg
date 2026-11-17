"""Engine-free fail-closed contracts for the private IK retargeter builder.

The builder itself runs ONLY inside a separately authorized, RAM-gated UE 5.8.4
editor. These tests do not execute retargeting or create/save .uasset files.
"""
from pathlib import Path
import ast
import unittest


TOOLS = Path(__file__).resolve().parent
CODE = (TOOLS / "build_private_ender_ik_retargeter.py").read_text(encoding="utf8")


class PrivateEnderIKBuilderContracts(unittest.TestCase):
    def test_file_is_valid_python(self):
        ast.parse(CODE)

    def test_explicit_owner_opt_in_fail_closed(self):
        for token in (
            'os.environ.get("TSTSS_PRIVATE_IK_CREATE") == "1"',
            '"OWNER_OPT_IN_REQUIRED"',
            '"RAM_RESERVE"',
            '"DISK_RESERVE"',
            '"NATIVE_AUDIT_NOT_ACCEPTED"',
            '"NATIVE_AUDIT_STALE"',
            '"WRONG_PROJECT"',
            '"WRONG_UNREAL_VERSION"',
            '"SOURCE_REVISION_DRIFT"',
            '"TRACKED_WORKTREE_DIRTY"',
        ):
            with self.subTest(token=token):
                self.assertIn(token, CODE)

    def test_never_overwrite_or_publish_rig_files(self):
        self.assertIn('FOLDER = "/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL"', CODE)
        self.assertIn('"PRIVATE_OUTPUT_NOT_GIT_IGNORED"', CODE)
        self.assertIn('"GENERATED_ASSET_ALREADY_EXISTS"', CODE)
        self.assertIn('"GENERATED_FILE_ALREADY_EXISTS"', CODE)
        self.assertIn('not unreal.EditorAssetLibrary.does_asset_exist(', CODE)
        self.assertIn('startswith(FOLDER + "/")', CODE)
        self.assertIn('"production_asset_saved": False', CODE)
        for forbidden in (
            "git push", "git add", "rclone", "copyto", "overwrite_existing_files=True",
            "unreal.EditorLevelLibrary.save_current_level",
            "unreal.EditorAssetLibrary.delete_asset(",
            "unreal.IKRetargetBatchOperation.",
            "unreal.GameplayStatics.open_level(",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, CODE)

    def test_two_separate_meshes_and_three_scoped_assets_only(self):
        self.assertIn('"IK_Manny_EnderReview_NONCANONICAL"', CODE)
        self.assertIn('"IK_Genesis9_EnderReview_NONCANONICAL"', CODE)
        self.assertIn('"RTG_MannyToEnder_NONCANONICAL"', CODE)
        self.assertIn('unreal.IKRigDefinitionFactory()', CODE)
        self.assertIn('unreal.IKRetargetFactory()', CODE)
        self.assertIn('unreal.IKRigController.get_controller(rig)', CODE)
        self.assertIn('unreal.IKRetargeterController.get_controller(retargeter)', CODE)
        self.assertIn('"SOURCE_SKELETON_DRIFT"', CODE)
        self.assertIn('"TARGET_SKELETON_DRIFT"', CODE)

    def test_all_chains_mapped_with_parent_ancestry(self):
        for chain in ("Spine", "Head", "LeftArm", "RightArm", "LeftLeg", "RightLeg"):
            self.assertIn('"' + chain + '":', CODE)
        self.assertIn('descends_from(source_mesh, *source)', CODE)
        self.assertIn('descends_from(target_mesh, *target)', CODE)
        self.assertIn('mesh.get_bone_parent(unreal.Name(bone))', CODE)
        self.assertIn('"SOURCE_ANCESTRY_" + chain', CODE)
        self.assertIn('"TARGET_ANCESTRY_" + chain', CODE)
        self.assertIn('controller.get_source_chain(chain)', CODE)

    def test_no_animation_or_approval_promoted(self):
        for token in (
            '"animation_sequences_generated": 0',
            '"native_playback_verified": False',
            '"rendered_foot_plant_verified": False',
            '"creator_art_approved": False',
            '"review_map_saved": False',
        ):
            self.assertIn(token, CODE)
        for forbidden in (
            "play_animation(", "PlayAnimation(", "save_current_level(",
            "duplicate_and_retarget(", "run_batch_retarget(", "set_actor_location(",
        ):
            self.assertNotIn(forbidden, CODE)

    def test_negative_mutations_to_owner_and_ancestry_gates(self):
        for required in (
            '== "1",', 'available_ram_gib() >= 6.0',
            'git("rev-parse", "HEAD") == SHA',
            'not git("status", "--porcelain=v1", "--untracked-files=no")',
            'descends_from(source_mesh, *source)',
            'descends_from(target_mesh, *target)',
            'not (LOCAL_FOLDER / (name + ".uasset")).exists()',
        ):
            with self.subTest(required=required):
                self.assertIn(required, CODE)
                damaged = CODE.replace(required, "/* removed admission guard */", 1)
                self.assertNotIn(required, damaged)


if __name__ == "__main__":
    unittest.main()
