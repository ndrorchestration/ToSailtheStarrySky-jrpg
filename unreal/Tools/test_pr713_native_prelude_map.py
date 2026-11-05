"""Source-only gate for the opt-in real Unreal Editor Prelude map verifier.

This runs on hosted Linux, NOT in UE or PIE. It tests fail-closed
source admission and prevents the native verifier becoming a tool for
editing player saves, committing map bytes or falsely declaring PIE.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import tempfile
import unittest
from unittest import mock

import verify_pr713_native_prelude_map as qa

PROJECT = Path(__file__).resolve().parents[1]


class NativeMapSourceGateTests(unittest.TestCase):
    def test_pinned_map_hash_matches_real_repository_artifact(self):
        self.assertEqual(
            hashlib.sha256((PROJECT / qa.MAP_RELATIVE).read_bytes()).hexdigest(),
            qa.MAP_SHA256,
        )
        self.assertEqual(qa.MAP_PACKAGE,
                         "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2")
        self.assertEqual(len(qa.STOP_SPECS), 7)

    def test_real_native_method_calls_and_pie_denial_are_explicit(self):
        text = Path(qa.__file__).read_text(encoding="utf-8")
        for token in (
            "unreal.EditorLoadingAndSavingUtils.load_map(MAP_PACKAGE)",
            "subsystem.get_all_level_actors()",
            "isinstance(a, unreal.TSTSSMilestoneActor)",
            "actor.get_component_by_class(unreal.StaticMeshComponent)",
            "unreal.TSTSSGameMode",
            "unreal.new_object(unreal.TSTSSFirstWakeState)",
            "verify_world_geometry(stop_actors, player_start, floor)",
            "layout.validate_plan()",
            "get_actor_scale3d()",
            '"world_layout_matches_authoring_plan": True',
            '"all_marker_footprints_on_floor": True',
            '"first_marker_initially_out_of_interaction_reach": True',
            "stop_actors[\"IoniaHiring\"].try_activate(state)",
            "state.get_review_objective_text()",
            "state.is_chapter_one_act_one()",
            "\"actual_pie_player_input_tested\": False",
            "\"actual_savegame_disk_roundtrip_tested\": False",
            "\"native_collision_line_trace_tested\": False",
            "\"render_or_water_physics_approved\": False",
            "\"character_or_ship_art_approved\": False",
        ):
            self.assertIn(token, text)
        for prohibited in (
            "save_map(",
            "save_asset(",
            "delete_game_in_slot(",
            "save_game_to_slot(",
            "execute_console_command(",
            "editor_request_begin_play(",
        ):
            self.assertNotIn(prohibited, text)

    def test_expected_source_boundary_has_narrow_worktree_name(self):
        self.assertEqual(qa.EXPECTED_PARENT, "TSTSS_PR713_NativeMapQA_20261102")
        self.assertEqual(qa.JOINED_EXPECTED_PARENT, "TSTSS_PR735_NativeMapQA_20261103")
        self.assertEqual(qa.ALLOWED_PARENTS,
                         {qa.EXPECTED_PARENT, qa.JOINED_EXPECTED_PARENT, qa.ASSEMBLY_EXPECTED_PARENT, qa.MAP_REPAIR_EXPECTED_PARENT, qa.MARKER_SAVE_JOIN_EXPECTED_PARENT})
        self.assertEqual(qa.LABEL_PREFIX, "TSTSS_PRELUDE_REVIEW_")

    def test_bad_checkout_and_wrong_commit_fail_closed_before_ue(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "UnexpectedPR" / "unreal"
            path.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "not the explicitly named"):
                qa.check_source(path, "a" * 40)
            good = Path(directory) / qa.EXPECTED_PARENT / "unreal"
            good.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "40 hex"):
                qa.check_source(good, "bad")

    def test_joined_pr735_root_reaches_exact_sha_gate_not_source_io(self):
        with tempfile.TemporaryDirectory() as directory:
            joined = Path(directory) / qa.JOINED_EXPECTED_PARENT / "unreal"
            joined.mkdir(parents=True)
            # The second allowed root is not authorization to skip SHA checks.
            with mock.patch.object(qa, "git", return_value="b" * 40):
                with self.assertRaisesRegex(RuntimeError, "SHA does not match"):
                    qa.check_source(joined, "a" * 40)
            impostor = Path(directory) / (qa.JOINED_EXPECTED_PARENT + "_copy") / "unreal"
            impostor.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "not the explicitly named"):
                qa.check_source(impostor, "a" * 40)

    def test_explicit_map_repair_root_still_requires_exact_head(self):
        with tempfile.TemporaryDirectory() as directory:
            good = Path(directory) / qa.MAP_REPAIR_EXPECTED_PARENT / "unreal"
            good.mkdir(parents=True)
            with mock.patch.object(qa, "git", return_value="b" * 40):
                with self.assertRaisesRegex(RuntimeError, "SHA does not match"):
                    qa.check_source(good, "a" * 40)
            impostor = Path(directory) / (qa.MAP_REPAIR_EXPECTED_PARENT + "_copy") / "unreal"
            impostor.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "not the explicitly named"):
                qa.check_source(impostor, "a" * 40)

    def test_join_workspace_requires_pin_and_rejects_suffix(self):
        with tempfile.TemporaryDirectory() as directory:
            exact = Path(directory) / qa.MARKER_SAVE_JOIN_EXPECTED_PARENT / "unreal"
            exact.mkdir(parents=True)
            with mock.patch.object(qa, "git", return_value="b" * 40):
                with self.assertRaisesRegex(RuntimeError, "SHA does not match"):
                    qa.check_source(exact, "a" * 40)
            renamed = Path(directory) / (qa.MARKER_SAVE_JOIN_EXPECTED_PARENT + "_copy") / "unreal"
            renamed.mkdir(parents=True)
            with self.assertRaisesRegex(RuntimeError, "not the explicitly named"):
                qa.check_source(renamed, "a" * 40)

    def test_dirty_worktree_refused_before_asset_io(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / qa.EXPECTED_PARENT / "unreal"
            p.mkdir(parents=True)
            def fake_git(root, *args):
                if args == ("rev-parse", "HEAD"):
                    return "a" * 40
                if args == ("status", "--porcelain"):
                    return " M unreal/Config/DefaultInput.ini"
                raise RuntimeError("Unexpected test git")
            with mock.patch.object(qa, "git", side_effect=fake_git):
                with self.assertRaisesRegex(RuntimeError, "dirty before map inspection"):
                    qa.check_source(p, "a" * 40)

    def test_wrong_head_refused_before_asset_io(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / qa.EXPECTED_PARENT / "unreal"
            p.mkdir(parents=True)
            with mock.patch.object(qa, "git", return_value="b" * 40):
                with self.assertRaisesRegex(RuntimeError, "SHA does not match"):
                    qa.check_source(p, "a" * 40)

    def test_worktree_custody_refuses_modified_head(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / qa.EXPECTED_PARENT / "unreal"
            (p / qa.MAP_RELATIVE).parent.mkdir(parents=True)
            (p / qa.MAP_RELATIVE).write_bytes(b"map")
            (p / "Config").mkdir()
            (p / "Config/DefaultEngine.ini").write_bytes(b"engine")
            (p / "Config/DefaultInput.ini").write_bytes(b"input")
            initial = {"head": "a" * 40,
                       "before_map_hash": qa.digest(p / qa.MAP_RELATIVE),
                       "config_hashes": {
                           "DefaultEngine.ini": qa.digest(p / "Config/DefaultEngine.ini"),
                           "DefaultInput.ini": qa.digest(p / "Config/DefaultInput.ini")}}
            with mock.patch.object(qa, "git", return_value="b" * 40):
                with self.assertRaisesRegex(RuntimeError, "Git commit changed"):
                    qa.final_custody(p, initial)
            (p / "Config/DefaultInput.ini").write_bytes(b"modified")
            with self.assertRaisesRegex(RuntimeError, "modified tracked default"):
                qa.final_custody(p, initial)

    def test_no_pie_or_savegame_false_positive_from_receipt(self):
        src = Path(qa.__file__).read_text(encoding="utf-8")
        self.assertIn('"NATIVE_EDITOR_MAP_AND_REAL_ACTORS_PASS_NOT_PIE"', src)
        self.assertIn('with destination.open("x"', src)
        self.assertIn('final_custody(project, before)', src)
        self.assertIn('TSTSS_REVIEW_EXPECTED_HEAD', src)


if __name__ == "__main__":
    unittest.main()
