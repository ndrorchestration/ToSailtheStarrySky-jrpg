"""Engine-free safety tests. Actual native image QA runs only on NEONTIC."""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = (ROOT / "native_rt_v2_lower_forehead_front.py").read_text(encoding="utf-8")
TRIAL = (ROOT / "native_rt_v2_lower_forehead_light_tenth_review_20261104.py").read_text(
    encoding="utf-8")
SWAPS = (
    ("RenderTargetV2LowerForehead04_LightsTenth", "RenderTargetV2LowerForehead02"),
    ("NATIVE_V2_TENTH_LIGHT_PNG_CORE_PASS_VISUAL_UNREVIEWED",
     "NATIVE_V5_GOGGLES_RENDER_TARGET_PNG_CORE_PASS_VISUAL_UNREVIEWED"),
    ('comp.set_editor_property("intensity",power*0.1)',
     'comp.set_editor_property("intensity",power)'),
)


def assert_single_variable(candidate):
    for changed, baseline in SWAPS:
        if candidate.count(changed) != 1:
            raise ValueError("FAIL_CLOSED missing or repeated source delta")
        candidate = candidate.replace(changed, baseline)
    if candidate != SOURCE:
        raise ValueError("FAIL_CLOSED unrelated source mutation")


class NativeV2LightingSourceTests(unittest.TestCase):
    def test_true_light_source_delta(self):
        assert_single_variable(TRIAL)

    def test_reject_unexpected_material_or_factor_change(self):
        with self.assertRaises(ValueError):
            assert_single_variable(TRIAL.replace('power*0.1', 'power*1.0'))
        with self.assertRaises(ValueError):
            assert_single_variable(TRIAL.replace('capture_source', 'save_current_level'))

    def test_refuse_existing_evidence_and_production_paths(self):
        for code in (SOURCE, TRIAL):
            self.assertIn('require(not OUT.exists()', code)
            self.assertIn('c:/mh5/castallsandbox', code)
            self.assertIn('production_game_modified":False', code)
            self.assertNotIn('save_current_level(', code)
            self.assertNotIn('save_loaded_asset(', code)

    def test_receipt_summary_not_art_approval(self):
        r = json.loads((ROOT / "Evidence/native_v2_lower_light_review_20261104.json")
                       .read_text(encoding="utf-8"))
        self.assertEqual(r["status"],
                         "NATIVE_V2_SEALED_GOGGLES_LOW_LIGHT_IMPROVES_READABILITY_ART_HOLD")
        self.assertFalse(r["goggles_physically_fitted"])
        self.assertFalse(r["facial_likeness_approved"])
        self.assertFalse(r["real_rig_approved"])
        self.assertTrue(r["review_only_noncanonical"])
        self.assertNotEqual(r["old_lighting"]["sha256_png_core"],
                            r["temporary_pointlight_x0p1"]["sha256_png_core"])
        self.assertGreater(r["white_clip_fraction_point_reduction"], 0.3)


if __name__ == "__main__":
    unittest.main()
