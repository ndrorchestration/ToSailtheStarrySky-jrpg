"""Portable adversarial source checks for First Wake lighting review."""
import dataclasses
import math
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tstss_lighting_review as mod

class LightingPlanTests(unittest.TestCase):
    def test_eleven_distinct_review_looks(self):
        plan = mod.validate()
        self.assertEqual(len(plan["looks"]), 11)
        self.assertEqual(plan["status"], "SOURCE_PLAN_ONLY_NO_NATIVE_OR_VISUAL_APPROVAL")
        self.assertFalse(plan["night_day_runtime_interpolation_implemented"])
        self.assertFalse(plan["water_contact_evidence_generated"])
        self.assertFalse(plan["production_content_modified"])

    def test_dusk_day_night_storm_and_interior_all_present(self):
        names = [look.name for look in mod.LOOKS]
        for required in ("harbor_day","harbor_dusk","harbor_night_review","engineering","bridge","ascent",
                         "auroral_twilight","phase_drift","storm_descent","sea_contact",
                         "shore_aftermath"):
            self.assertIn(required, names)
        self.assertLess(names.index("sea_contact"), names.index("shore_aftermath"))

    def test_each_destination_is_new_review_namespace(self):
        for look in mod.LOOKS:
            dest = mod.destination(look.name)
            self.assertTrue(dest.startswith("/Game/TSTSS/Review/Lighting/"))
            self.assertNotEqual(dest, mod.BASE_MAP)

    def test_unknown_destination_denied(self):
        with self.assertRaises(ValueError):
            mod.destination("../Production/Default")
        with self.assertRaises(ValueError):
            mod.stage_native("Starbourne_Unlock")

    def test_negative_brightness_rejected(self):
        bad = dataclasses.replace(mod.LOOKS[0], sun_lux=-1)
        with self.mock_looks((bad,)+mod.LOOKS[1:]):
            with self.assertRaisesRegex(ValueError, "luminance"):
                mod.validate()

    def test_nan_and_fog_overflow_rejected(self):
        for bad in (dataclasses.replace(mod.LOOKS[0], fog_density=math.nan),
                    dataclasses.replace(mod.LOOKS[0], fog_density=.8),
                    dataclasses.replace(mod.LOOKS[0], exposure_bias_ev=40)):
            with self.subTest(bad=bad):
                with self.mock_looks((bad,)+mod.LOOKS[1:]):
                    with self.assertRaises(ValueError):
                        mod.validate()

    def test_duplicate_look_rejected(self):
        bad = (mod.LOOKS[0],mod.LOOKS[0])+mod.LOOKS[2:]
        with self.mock_looks(bad):
            with self.assertRaises(ValueError):
                mod.validate()

    def test_lost_story_sequence_rejected(self):
        bad = list(mod.LOOKS)
        bad[-1],bad[-2] = bad[-2],bad[-1]
        with self.mock_looks(tuple(bad)):
            with self.assertRaisesRegex(ValueError, "Aftermath"):
                mod.validate()

    def test_only_dedicated_worktree_is_writable(self):
        with self.assertRaises(RuntimeError):
            mod.check_disposable_project(r"C:\TSTSS_Convergence_20261110\unreal")
        with self.assertRaises(RuntimeError):
            mod.check_disposable_project(r"C:\TSTSS_Lighting_20261110\other")

    class mock_looks:
        def __init__(self,new): self.new=new
        def __enter__(self):
            self.old=mod.LOOKS
            mod.LOOKS=self.new
        def __exit__(self,*unused):
            mod.LOOKS=self.old

if __name__ == "__main__":
    unittest.main()
