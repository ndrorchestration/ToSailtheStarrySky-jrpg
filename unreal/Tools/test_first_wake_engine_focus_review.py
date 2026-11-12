"""Source-only positive/negative checks for isolated First Wake engine bokeh.

No Unreal import, map mutation, editor launch or gameplay simulation.
"""
import copy
from pathlib import Path
import unittest
from unittest.mock import patch

import stage_first_wake_engine_focus_review as stage


class EngineFocusStagingContractTests(unittest.TestCase):
    def test_plan_is_isolated_and_receiver_off(self):
        plan = stage.plan()
        self.assertEqual(plan["status"], "SOURCE_PLAN_ONLY_NO_NATIVE_MAP_OR_PIE")
        self.assertEqual(plan["new_camera_count"], 4)
        self.assertEqual(plan["new_receivers"], 1)
        self.assertFalse(plan["receivers_enabled"])
        self.assertFalse(plan["auto_switches_player_camera"])
        self.assertEqual(plan["source_map"],
                         "/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors")
        self.assertEqual(plan["target_review_map"],
                         "/Game/TSTSS/Review/EngineFocus_V1/M_EnginePresentationReview")

    def test_source_only_self_test_is_not_native_evidence(self):
        result = stage.self_test()
        self.assertEqual(result["status"], "ENGINE_FOCUS_OFFLINE_PREFLIGHT_PASS")
        self.assertFalse(result["native_map_created"])
        self.assertEqual(result["native_compilation"], "NOT_RUN")

    def test_source_destination_collision_denied(self):
        with patch.object(stage, "SOURCE", stage.DEST):
            with self.assertRaisesRegex(RuntimeError, "destination"):
                stage.plan()

    def test_review_root_namespace_cannot_collide_with_harbor(self):
        with patch.object(stage, "DEST_ROOT",
                          "/Game/TSTSS/Review/DynamicFocus_V1"):
            with self.assertRaisesRegex(RuntimeError, "harbor"):
                stage.plan()

    def test_duplicate_camera_name_denied(self):
        with patch.object(stage, "CAMERAS",
                          ("A", "B", "B", "D")):
            with self.assertRaisesRegex(RuntimeError, "distinct"):
                stage.plan()

    def test_collision_between_receiver_and_cine_camera_denied(self):
        with patch.object(stage, "RECEIVER", stage.CAMERAS[1]):
            with self.assertRaisesRegex(RuntimeError, "review map mismatch"):
                stage.plan()

    def test_unreviewed_engine_aperture_denied(self):
        data = copy.deepcopy(stage.profile_data())
        for shot in data["shots"]:
            if shot["id"] == "FW03_Engine_Inspection":
                shot["f_stop"] = 1.0
        with patch.object(stage, "profile_data", return_value=data):
            with self.assertRaisesRegex(RuntimeError, "inspector lens"):
                stage.plan()

    def test_unreviewed_engine_reveal_lens_denied(self):
        data = copy.deepcopy(stage.profile_data())
        for shot in data["shots"]:
            if shot["id"] == "FW04_Engine_Awakening":
                shot["lens_mm"] = 135
        with patch.object(stage, "profile_data", return_value=data):
            with self.assertRaisesRegex(RuntimeError, "reveal lens"):
                stage.plan()

    def test_src_code_uses_save_map_as_and_fresh_process(self):
        text = Path(stage.__file__).read_text(encoding="utf-8")
        self.assertIn("EditorLoadingAndSavingUtils.save_map(source_world, DEST)", text)
        self.assertNotIn("EditorAssetLibrary.duplicate_asset(", text)
        self.assertIn('TSTSS_ENGINE_FOCUS_EXPECTED_HEAD', text)
        self.assertIn('TSTSS_ENGINE_FOCUS_STAGE_EXPLICIT', text)
        self.assertIn('TSTSS_ENGINE_FOCUS_PHASE', text)
        self.assertIn('get_editor_property("explicit_review_opt_in")', text)
        self.assertIn("receiver_remains_disabled", text)
        self.assertIn("protected_config_sha256", text)

    def test_custody_refuses_unsolicited_native_staging(self):
        # Never enter a native Editor action. Custody is read-only and must
        # refuse when authorization variables are deliberately absent.
        with patch.dict(stage.os.environ, {
            "TSTSS_ENGINE_FOCUS_EXPECTED_HEAD": "",
            "TSTSS_ENGINE_FOCUS_STAGE_EXPLICIT": ""
        }):
            with self.assertRaises(RuntimeError):
                stage.custody("prepare")


if __name__ == "__main__":
    unittest.main()
