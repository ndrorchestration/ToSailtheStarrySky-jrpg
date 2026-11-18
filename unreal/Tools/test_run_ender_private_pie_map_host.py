"""Engine-free safety contract checks for the guarded private map authoring host."""
import importlib.util
import sys
import unittest
from pathlib import Path

PATH = Path(__file__).with_name("run_ender_private_pie_map_host.py")
S = PATH.read_text(encoding="utf8")
spec = importlib.util.spec_from_file_location("ender_pie_host", PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

class HostTests(unittest.TestCase):
    def test_no_user_process_termination_except_owned_child(self):
        self.assertIn('"/PID", str(child.pid)', S)
        self.assertIn('must(not active_unreal(), "OTHER_UNREAL_PROCESS")', S)
        self.assertNotIn("taskkill /IM", S)
        self.assertIn('"-nullrhi"', S)

    def test_release_not_claimed(self):
        for token in ('"pie_playback_verified": False', '"creator_approved": False',
                      '"PRIVATE_PIE_MAP_STAGE_PASS_NOT_PLAYBACK_ACCEPTED"'):
            self.assertIn(token, S)

    def test_exact_head_recheck_and_custody(self):
        for token in ('native_38_verified(head)', '"EXACT_HEAD_NATIVE_38_REQUIRED"',
                      'not git("status", "--porcelain=v1")',
                      '"protected_hashes_unchanged"', '"PRIVATE_NOT_GIT_IGNORED"',
                      '"PRIVATE_OUTPUT_COLLISION"', '"report_fresh"'):
            self.assertIn(token, S)

    def test_bound_startup_runtime_resources(self):
        self.assertEqual((mod.START_RAM, mod.START_DISK), (6.5, 16.5))
        self.assertEqual((mod.RUN_RAM, mod.RUN_DISK), (2.5, 14.3))
        self.assertLessEqual(mod.MAX_TIME_S, 300)

    def test_exact_expected_private_output_set(self):
        self.assertEqual(mod.EXPECTED,
                         {"BP_EnderPIEGameMode_NONCANONICAL.uasset",
                          "FirstWake_PreludeInteraction_V5_VisualReview.umap"})

if __name__ == "__main__":
    unittest.main()
