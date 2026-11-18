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
            '"HOST_STARTUP_RESERVE_UNPROVEN"',
            '"MISSING_HOST_STARTUP_GATE"',
            '"HOST_STARTUP_GATE_MISMATCH"',
            '"HOST_STARTUP_GATE_STALE"',
            '"RAM_RUNTIME_FLOOR"',
            '"DISK_RUNTIME_FLOOR"',
            '"NATIVE_AUDIT_NOT_ACCEPTED"',
            '"NATIVE_AUDIT_STALE"',
            '"WRONG_PROJECT"',
            '"WRONG_UNREAL_VERSION"',
            '"SOURCE_NATIVE_ANCESTOR_DRIFT"',
            '"NATIVE_AUDIT_HEAD_MISMATCH"',
            '"PRIVATE_OR_TEMPLATE_FILE_HASH_DRIFT_"',
            '"TRACKED_WORKTREE_DIRTY"',
        ):
            with self.subTest(token=token):
                self.assertIn(token, CODE)

    def test_two_stage_host_resource_admission_not_reflexive(self):
        self.assertIn('STARTUP_GATE = PROJECT /', CODE)
        self.assertIn('startup.get("mode") == "create-rigs"', CODE)
        self.assertIn('available_ram_gib() >= 2.5', CODE)
        self.assertNotIn('available_ram_gib() >= 6.0', CODE)
        self.assertIn('shutil.disk_usage("C:\\\\").free >= 14.3 * 2**30', CODE)

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
        self.assertIn('controller.add_default_ops()', CODE)
        self.assertIn('controller.get_num_retarget_ops() >= 5', CODE)
        self.assertIn('"RETARGETER_HAS_NO_FK_IK_CHAIN_OPS"', CODE)
        self.assertIn('"RETARGET_CHAIN_SET_" + chain', CODE)
        self.assertIn('"SOURCE_FILE_CHANGED_DURING_IK_CREATE"', CODE)

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

    def test_self_referential_git_hash_is_not_used(self):
        self.assertNotIn('SHA = "2235f3a4283f93a12f5d3e85ce1a8039b2c865b3"', CODE)
        self.assertIn('VALIDATED_NATIVE_ANCESTOR =', CODE)
        self.assertIn('audit.get("source_head") == head', CODE)
        self.assertIn('merge-base", "--is-ancestor"', CODE)

    def test_manny_package_root_is_exact_internal_ue_template_root(self):
        self.assertIn('MANNY = "/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"', CODE)
        self.assertIn('"Characters/Mannequins/Meshes/SK_Mannequin.uasset"', CODE)
        self.assertIn('"Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset"', CODE)
        self.assertNotIn('"/Game/Mannequins/', CODE)

    def test_all_source_and_private_inputs_rehashed(self):
        for path in (
            "SKM_Manny_Simple.uasset", "SK_Mannequin.uasset",
            "MM_Idle.uasset", "MF_Unarmed_Walk_Fwd.uasset",
            "MF_Unarmed_Jog_Fwd.uasset",
            "Genesis9_BaseShirtShorts_MergedRig_REVIEW.uasset",
            "Genesis9_BaseShirtShorts_MergedRig_REVIEW_Skeleton.uasset",
        ):
            self.assertIn(path, CODE)
        self.assertIn('hash_file(file_path) == expected', CODE)
        self.assertIn('SOURCE_FILE_CHANGED_DURING_IK_CREATE', CODE)

    def test_negative_mutations_to_owner_and_ancestry_gates(self):
        for required in (
            '== "1",', 'available_ram_gib() >= 2.5',
            'startup.get("ram_start_gib", 0) >= 6.5',
            'startup.get("disk_start_gib", 0) >= 16.5',
            'startup.get("run_id") == os.environ.get("TSTSS_PRIVATE_IK_RUN_ID")',
            'audit.get("source_head") == head',
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
