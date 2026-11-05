"""Engine-free safety and custody tests for separate Harbor readback launcher."""
import inspect
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import run_first_wake_harbor_native_readback as readback
import run_first_wake_harbor_native_stage as stage


class HarborReadbackRunnerContracts(unittest.TestCase):
    def test_uses_stage_approved_sandbox_paths_and_hashes(self):
        self.assertEqual(readback.ROOT, stage.ROOT)
        self.assertEqual(readback.PROJECT, stage.PROJECT)
        self.assertEqual(readback.ENGINE, stage.EDITOR)
        self.assertEqual(readback.STAGE_NATIVE, stage.NATIVE)
        self.assertEqual(readback.STAGE_HOST, stage.HOST)
        self.assertEqual(readback.MIN_NATIVE_GIB, stage.MIN_NATIVE_GIB)
        self.assertEqual(readback.MIN_DISK_GIB, stage.MIN_FREE_DISK_GIB)

    def test_native_preflight_requires_dual_stage_receipts(self):
        src = inspect.getsource(readback.readback_preflight)
        for gate in (
            '"NATIVE_MAP_SAVED_PENDING_INDEPENDENT_READBACK"',
            '"NATIVE_HARBOR_MAP_SAVED_PENDING_INDEPENDENT_READBACK"',
            'map_hash != host.get("new_map_sha256")',
            'map_hash != native.get("map_sha256")',
            'stage.git("rev-parse", "HEAD")',
            'stage.EXPECTED_MAP_SHA',
        ):
            self.assertIn(gate, src)
        self.assertIn("config_hashes != host.get", src)

    def test_no_editor_or_live_coding_concurrency(self):
        src = inspect.getsource(readback.readback_preflight)
        for process in ("unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe"):
            self.assertIn(process, src)
        self.assertIn("stage.free_gib()", src)
        self.assertIn("shutil.disk_usage(ROOT)", src)

    def test_existing_readback_files_cannot_be_overwritten(self):
        src = inspect.getsource(readback.readback_preflight)
        for file in ("READBACK_NATIVE", "READBACK_HOST", "READBACK_LOG",
                     "READBACK_CONSOLE"):
            self.assertIn(file, src)
        self.assertIn("prior native readback exists, no overwrite", src)
        self.assertIn("SaveGames", src)

    def test_starts_only_headless_readback_not_pie_or_gpu(self):
        src = inspect.getsource(readback.main)
        self.assertIn('"-NullRHI"', src)
        self.assertIn("READBACK_LOG", src)
        self.assertNotIn("-RenderOffscreen", src)
        self.assertNotIn('"-game"', src)
        self.assertNotIn("save_current_level", src)

    def test_exit_log_receipt_and_preservation_required(self):
        src = inspect.getsource(readback.main)
        for guard in (
            'INDEPENDENT_NATIVE_HARBOR_SAVED_WORLD_READBACK_PASS_NOT_PIE',
            'TSTSS_HARBOR_INDEPENDENT_READBACK_PASS_NOT_PIE',
            'verified.get("total_actor_count") != 84',
            'verified.get("new_materials_verified") != 8',
            "config_hashes_preserved",
            "parent_map_sha_preserved",
            "staged_map_sha_preserved",
            "source_head_preserved",
        ):
            self.assertIn(guard, src)

    def test_only_own_readback_child_can_be_stopped(self):
        src = inspect.getsource(readback.main)
        self.assertIn("proc.terminate()", src)
        self.assertIn("proc.kill()", src)
        self.assertNotIn("taskkill", src)
        self.assertNotIn("Stop-Process", src)
        self.assertGreaterEqual(readback.MAX_RUNTIME_S, 120)
        self.assertLessEqual(readback.MAX_RUNTIME_S, 300)

    def test_review_not_approving_art_or_runtime(self):
        src = inspect.getsource(readback.readback_preflight)
        for negative in ('"native_gpu_capture_verified": False',
                         '"pie_verified": False', '"creator_art_approved": False',
                         '"starbourne_unlocked": False'):
            self.assertIn(negative, src)

    def test_no_native_run_on_unsupported_host(self):
        with patch.object(sys, "platform", "linux"):
            with self.assertRaisesRegex(RuntimeError, "isolated Windows worktree"):
                readback.readback_preflight()

    def test_native_verifier_import_handles_unreal_working_directory(self):
        text = Path(__file__).with_name("verify_first_wake_harbor_native.py").read_text(encoding="utf-8")
        self.assertIn("Path(__file__).resolve().parent", text)
        self.assertIn("sys.path.insert(0, TOOLS_DIR)", text)


if __name__ == "__main__":
    unittest.main()
