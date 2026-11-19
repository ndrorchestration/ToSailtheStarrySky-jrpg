"""Pure Python regression tests for UE benchmark data and safety boundaries."""
import importlib.util
import pathlib
import subprocess
import sys
import unittest

HERE = pathlib.Path(__file__).resolve()
SCRIPT = HERE.parents[1] / "Tools" / "build_first_wake_benchmark.py"
spec = importlib.util.spec_from_file_location("first_wake_benchmark", SCRIPT)
benchmark = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = benchmark
spec.loader.exec_module(benchmark)

class BenchmarkPlanTests(unittest.TestCase):
    def test_layout_is_valid_and_deterministic(self):
        self.assertEqual(benchmark.validate_plan(), benchmark.validate_plan())
        self.assertEqual(len(benchmark.PIECES), 15)
        self.assertEqual(len(benchmark.CAMERAS), 4)
        self.assertEqual(len(benchmark.IMPORT_SLOTS), 4)

    def test_real_ship_component_is_reused(self):
        self.assertEqual(benchmark.SHIP_CLASS_PATH,
                         "/Script/ToSailTheStarrySky.AureateWakePreviewActor")
        self.assertIn("NO_GAMEPLAY_OR_WATER_AUTHORITY",
                      benchmark.validate_plan()["authority"])

    def test_preflight_does_not_spoil_recruitment(self):
        names = [name.lower() for name, _ in benchmark.IMPORT_SLOTS]
        self.assertEqual(len([n for n in names if "ender" in n]), 1)
        self.assertEqual(len([n for n in names if "ionia" in n]), 1)
        for name in names:
            self.assertNotIn("lyra", name)
            self.assertNotIn("talen", name)
            self.assertNotIn("reson", name)
            self.assertNotIn("aepex", name)

    def test_camera_aim_is_finite_and_not_degenerate(self):
        for cam in benchmark.CAMERAS:
            r = benchmark.look_at_rotation(cam.location, cam.target)
            self.assertTrue(all(-180 <= v <= 180 for v in r))
        with self.assertRaises(ValueError):
            benchmark.look_at_rotation((0, 0, 0), (0, 0, 0))

    def test_fail_closed_map_and_placement_boundaries(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("does_asset_exist(MAP_PATH)", source)
        self.assertIn("get_dirty_map_packages()", source)
        self.assertIn("new_blank_map(False)", source)
        self.assertIn("save_map(world, MAP_PATH)", source)
        self.assertNotIn("RequestForm(", source.replace("# Deliberately do not RequestForm:", ""))
        self.assertNotIn("AdvanceTo(", source)
        self.assertNotIn("FlotationConfirmed(", source)

    def test_normal_python_validation_does_not_import_unreal(self):
        p = subprocess.run([sys.executable, str(SCRIPT), "--validate"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("REVIEW_ONLY", p.stdout)

    def test_existing_asset_will_not_be_overwritten(self):
        source = SCRIPT.read_text(encoding="utf-8")
        self.assertLess(source.index("does_asset_exist(MAP_PATH)"),
                        source.index("new_blank_map(False)"))

if __name__ == "__main__":
    unittest.main()
