"""Engine-free guards for the optional UE NullRHI environment stage.

These never start UE, stop a process, create native assets, or read SaveGames.
"""
import inspect
import unittest
from unittest.mock import patch
import build_first_wake_harbor_environment as harbor
import run_first_wake_harbor_native_stage as runner


class HarborNativeRunnerContracts(unittest.TestCase):
    def test_worktree_scoped_and_exact_engine_required(self):
        self.assertEqual(runner.ROOT.name, "TSTSS_EnvironmentHarbor_20261104")
        self.assertEqual(runner.EXPECTED_BRANCH, "review/ue58-firstwake-environments-20261104")
        self.assertIn("5.8", str(runner.EDITOR))
        self.assertEqual(runner.EXPECTED_MAP_SHA, harbor.BASE_SHA256)

    def test_no_duplicate_existing_actors_or_maps(self):
        src = inspect.getsource(runner.native_preflight)
        self.assertIn("OUTPUT_MAP, NATIVE, HOST, LOG, CONSOLE", src)
        self.assertIn("digest(MAP) != EXPECTED_MAP_SHA", src)
        self.assertIn('git("status", "--porcelain", "--untracked-files=no")', src)
        self.assertIn("SaveGames", src)

    def test_in_use_editor_is_a_hard_refusal(self):
        src = inspect.getsource(runner.native_preflight)
        for name in ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe"):
            self.assertIn(name, src)

    def test_zero_graphics_claim_and_minimum_resources(self):
        self.assertEqual(runner.MIN_NATIVE_GIB, 5.0)
        self.assertEqual(runner.MIN_FREE_DISK_GIB, 14.0)
        src = inspect.getsource(runner.native_preflight)
        self.assertIn("free_gib()", src)
        self.assertIn("shutil.disk_usage(ROOT)", src)
        self.assertIn('"native_render_verified": False', src)
        self.assertIn('"pie_verified": False', src)

    def test_launch_nullrhi_only_never_gpu_or_pie(self):
        src = inspect.getsource(runner.main)
        self.assertIn('"-NullRHI"', src)
        self.assertNotIn("-game", src)
        self.assertNotIn("-RenderOffscreen", src)
        self.assertIn("TSTSS_HARBOR_BUILD_EXPLICIT", src)

    def test_only_own_child_can_be_terminated(self):
        src = inspect.getsource(runner.main)
        self.assertIn("proc.terminate()", src)
        self.assertIn("proc.kill()", src)
        self.assertNotIn("taskkill", src)
        self.assertNotIn("Stop-Process", src)

    def test_protected_configs_restored_and_verified(self):
        src = inspect.getsource(runner.main)
        self.assertIn("os.chmod(path, stat.S_IREAD)", src)
        self.assertIn("os.chmod(path, stat.S_IWRITE | stat.S_IREAD)", src)
        self.assertIn("config_hashes_preserved", src)
        self.assertIn("source_head_preserved", src)
        self.assertIn("parent_map_sha_preserved", src)

    def test_zero_timeout_will_not_change_safety_contract(self):
        self.assertGreaterEqual(runner.MAX_RUNTIME_S, 120)
        self.assertLessEqual(runner.MAX_RUNTIME_S, 300)

    def test_explicit_build_sentinel_without_ue_import_in_source_check(self):
        with patch.dict("os.environ", {"TSTSS_HARBOR_BUILD_EXPLICIT": "1"}):
            with patch.object(harbor, "build_in_unreal", return_value={"source_mock_only": True}) as build:
                import contextlib, io
                with contextlib.redirect_stdout(io.StringIO()):
                    harbor.main(["--validate"])
                build.assert_not_called()
                with contextlib.redirect_stdout(io.StringIO()):
                    harbor.main(None)
                build.assert_called_once()


if __name__ == "__main__":
    unittest.main()
