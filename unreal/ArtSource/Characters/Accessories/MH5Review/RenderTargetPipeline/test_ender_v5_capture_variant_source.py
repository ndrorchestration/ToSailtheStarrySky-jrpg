"""Engine-free source and provenance guards for separate Ender V5 captures.

These tests never run Unreal and never assert renderer success from CI.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASELINE = (ROOT / "native_rt_ender_v5_goggles01.py").read_text(encoding="utf-8")
STATUS_BASE = "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"

MANUAL_INSERT = """    # Test one exposure *mode*, not an approval of native material behavior.
    pp=cap.get_editor_property("post_process_settings")
    pp.set_editor_property("override_auto_exposure_method",True)
    pp.set_editor_property("auto_exposure_method",unreal.AutoExposureMethod.AEM_MANUAL)
    pp.set_editor_property("override_auto_exposure_bias",True)
    pp.set_editor_property("auto_exposure_bias",-2.0)
    cap.set_editor_property("post_process_settings",pp)
    cap.set_editor_property("post_process_blend_weight",1.0)
    record["manual_exposure_diagnostic_requested"]=True
"""


def undo_exact_variant(filename, changes, removed_block=None):
    text = (ROOT / filename).read_text(encoding="utf-8")
    for new, old in changes:
        if text.count(new) != 1:
            raise AssertionError("FAIL_CLOSED variant token count " + new)
        text = text.replace(new, old)
    if removed_block is not None:
        if text.count(removed_block) != 1:
            raise AssertionError("FAIL_CLOSED added block not unique")
        text = text.replace(removed_block, "")
    if text != BASELINE:
        raise AssertionError("FAIL_CLOSED variant changed unapproved source")
    return True


class EnderCaptureVariantSourceTests(unittest.TestCase):
    def test_basecolor_changes_capture_source_only(self):
        undo_exact_variant(
            "native_rt_ender_v5_goggles_basecolor_diag_20261104.py",
            [
                ("RenderTargetCombined04_BaseColor", "RenderTargetCombined02"),
                ("NATIVE_V5_GOGGLES_BASECOLOR_PNG_CORE_PASS_VISUAL_UNREVIEWED", STATUS_BASE),
                ("SceneCapture2D SCS_BASE_COLOR diagnostic -> RenderingLibrary.export_render_target",
                 "SceneCapture2D -> RenderingLibrary.export_render_target"),
                ("SCS_BASE_COLOR", "SCS_FINAL_COLOR_LDR"),
            ])

    def test_manual_exposure_is_isolated_trial(self):
        undo_exact_variant(
            "native_rt_ender_v5_goggles_manual_exposure_20261104.py",
            [
                ("RenderTargetCombined05_ManualExposure", "RenderTargetCombined02"),
                ("NATIVE_V5_GOGGLES_MANUAL_EXPOSURE_PNG_CORE_PASS_VISUAL_UNREVIEWED",
                 STATUS_BASE),
            ],
            MANUAL_INSERT)

    def test_tenth_light_is_isolated_trial(self):
        undo_exact_variant(
            "native_rt_ender_v5_goggles_light_tenth_20261104.py",
            [
                ("RenderTargetCombined06_LightTenth", "RenderTargetCombined02"),
                ("NATIVE_V5_GOGGLES_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED",
                 STATUS_BASE),
                ('comp.set_editor_property("intensity",power*0.1)',
                 'comp.set_editor_property("intensity",power)'),
            ])

    def test_defense_against_unsafe_script_mutation(self):
        original = ROOT / "native_rt_ender_v5_goggles_light_tenth_20261104.py"
        script = original.read_text(encoding="utf-8")
        self.assertIn('power*0.1', script)
        tampered = script.replace('power*0.1', 'power*10.0')
        self.assertEqual(tampered.count('power*0.1'), 0)
        self.assertNotEqual(tampered, script)
        self.assertIn('require(not OUT.exists()', BASELINE)
        self.assertIn('production_game_modified":False', BASELINE)
        self.assertIn('no_face_sculpt":True', BASELINE)
        for suffix in ("", "_basecolor_diag_20261104", "_manual_exposure_20261104",
                       "_light_tenth_20261104"):
            file = ("native_rt_ender_v5_goggles" + (suffix or "01") + ".py")
            if suffix == "_basecolor_diag_20261104":
                file = "native_rt_ender_v5_goggles_basecolor_diag_20261104.py"
            if suffix == "":
                file = "native_rt_ender_v5_goggles01.py"
            source = (ROOT / file).read_text(encoding="utf-8")
            self.assertNotIn("save_current_level(", source)
            self.assertNotIn("save_loaded_asset(", source)
            self.assertIn('require(ROOT.as_posix().lower()=="c:/mh5/castallsandbox"', source)

    def test_committed_native_receipt_summaries_are_conservative(self):
        base = json.loads(
            (ROOT / "Evidence/ender_v5_basecolor_comparison_20261104.json").read_text())
        matrix = json.loads(
            (ROOT / "Evidence/ender_v5_native_capture_matrix_20261104.json").read_text())
        self.assertEqual(base["status"], "NATIVE_BASECOLOR_DIAGNOSTIC_PASS_ART_HOLD")
        self.assertEqual(matrix["status"],
                         "ACTUAL_UE584_TENTH_LIGHT_REDUCES_FINALCOLOR_CLIPPING_ART_HOLD")
        self.assertIs(base["canon_promotion"], False)
        self.assertIs(matrix["no_canon_promotion"], True)
        self.assertIs(matrix["face_approved"], False)
        self.assertIs(matrix["goggles_v2_fit_approved"], False)
        self.assertIs(matrix["goggles_v1_creator_rejected_as_glasses"], True)
        self.assertIs(matrix["lower_light_is_pixel_distinct"], True)
        self.assertIs(matrix["manual_exposure_is_pixel_identical"], True)
        original = matrix["native_captures"]["baseline_final"]
        lowered = matrix["native_captures"]["tenth_temporary_light"]
        self.assertGreater(original["crop_nearwhite_fraction"], 0.5)
        self.assertLess(lowered["crop_nearwhite_fraction"], 0.001)
        self.assertEqual(
            matrix["native_captures"]["manual_minus2_ev"]["png_core_sha256"],
            original["png_core_sha256"])
        self.assertNotEqual(lowered["png_core_sha256"], original["png_core_sha256"])


if __name__ == "__main__":
    unittest.main()
