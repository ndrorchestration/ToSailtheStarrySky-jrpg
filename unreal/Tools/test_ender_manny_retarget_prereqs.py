"""Engine-free guard contracts for Ender Manny->Genesis9 retarget intake.

These tests verify that the native-only audit cannot mutate review assets or
infer finished animation from source filenames. They are not Unreal tests.
"""
from pathlib import Path
import ast
import re
import unittest
from types import SimpleNamespace


SOURCE = (Path(__file__).resolve().parent /
          "inspect_ender_manny_retarget_prereqs.py").read_text(encoding="utf8")


class EnderRetargetPrerequisiteContracts(unittest.TestCase):
    def test_native_audit_is_syntactically_valid(self):
        ast.parse(SOURCE)

    def test_all_three_distinct_locomotion_roles(self):
        self.assertIn('"idle": "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle"', SOURCE)
        self.assertIn('"walk": "/Game/Characters/Mannequins/Anims/Unarmed/Walk/MF_Unarmed_Walk_Fwd"', SOURCE)
        self.assertIn('"run_candidate": "/Game/Characters/Mannequins/Anims/Unarmed/Jog/MF_Unarmed_Jog_Fwd"', SOURCE)
        self.assertIn('SOURCE_TARGET_SKELETON_COLLISION', SOURCE)
        self.assertIn('CLIP_NOT_SOURCE_SKELETON_', SOURCE)
        self.assertIn('source_root_motion_roles', SOURCE)
        self.assertIn('"direct_source_clip_assignment_allowed"] = False', SOURCE)
        self.assertIn('PRIVATE_CONVERSION_AND_MEASUREMENT_REQUIRED', SOURCE)
        self.assertIn('"NATIVE_RETARGET_INPUTS_VALIDATED_NOT_RETARGETED"', SOURCE)
        self.assertIn('"source_clip_conversion_required"] = source_motion_requires_conversion', SOURCE)
        self.assertIn('"rig_compatibility_validated"] = True', SOURCE)
        self.assertNotIn('require(not root_motion,', SOURCE)

    def test_source_package_root_matches_epic_template_internal_references(self):
        self.assertNotIn('/Game/Mannequins/', SOURCE)
        self.assertIn('"/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple"', SOURCE)
        self.assertIn('"Characters/Mannequins/Meshes/SK_Mannequin.uasset"', SOURCE)
        self.assertIn('"Characters/Mannequins/Anims/Unarmed/MM_Idle.uasset"', SOURCE)

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
        self.assertIn("CHAIN_ANCESTRY_INVALID_", SOURCE)
        self.assertIn("trace_ancestry(source, src[0], src[1])", SOURCE)
        self.assertIn("trace_ancestry(target, tgt[0], tgt[1])", SOURCE)
        self.assertIn("cursor in seen", SOURCE)
        self.assertIn("mesh.get_bone_parent(unreal.Name(cursor))", SOURCE)
        self.assertIn("IK_RIG_EDITOR_PLUGIN_MISSING", SOURCE)


    def test_real_algorithm_accepts_valid_target_bone_ancestry(self):
        tree = ast.parse(SOURCE)
        fn = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and
                  node.name == "trace_ancestry")
        module = ast.Module(body=[fn], type_ignores=[])
        namespace = {"unreal": SimpleNamespace(Name=str)}
        exec(compile(module, "<isolated-trace-ancestry>", "exec"), namespace)
        trace = namespace["trace_ancestry"]
        class FakeMesh:
            def __init__(self, parents):
                self.parents = parents
            def get_bone_parent(self, name):
                return self.parents.get(str(name), "None")
        parents = {
            "l_toes": "l_foot", "l_foot": "l_shin",
            "l_shin": "l_thigh", "l_thigh": "pelvis",
            "l_hand": "l_forearm", "l_forearm": "l_upperarm",
            "l_upperarm": "l_shoulder",
        }
        mesh = FakeMesh(parents)
        self.assertEqual(
            trace(mesh, "l_thigh", "l_toes"),
            ["l_toes", "l_foot", "l_shin", "l_thigh"],
        )
        self.assertEqual(
            trace(mesh, "l_upperarm", "l_hand"),
            ["l_hand", "l_forearm", "l_upperarm"],
        )
        self.assertIsNone(trace(mesh, "r_thigh", "l_toes"))
        self.assertIsNone(trace(mesh, "l_upperarm", "l_toes"))
        self.assertIsNone(trace(mesh, "l_thigh", "missing_toe"))
        cycle = FakeMesh({"a": "b", "b": "a"})
        self.assertIsNone(trace(cycle, "pelvis", "a"))
        self.assertIsNone(trace(mesh, "pelvis", "missing_bone"))
        too_deep = FakeMesh(
            {f"b{i}": f"b{i+1}" for i in range(100)}
        )
        self.assertIsNone(trace(too_deep, "pelvis", "b0"))

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
