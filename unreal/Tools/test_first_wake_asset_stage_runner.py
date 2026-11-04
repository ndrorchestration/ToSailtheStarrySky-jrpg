"""Non-native resource/custody contracts for disposable asset stage runner."""
import ast
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name("run_first_wake_asset_stage.py")


class AssetStageRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = RUNNER.read_text(encoding="utf-8")
        ast.parse(cls.source)

    def test_source_asset_sha_custody_and_hard_limits(self):
        for token in (
            "TSTSS_AssetAssembly_20261104", "get_engine_version",
            "source.is_file() or not target.is_file() or sha(source) != sha(target)",
            "free_gib() < 5.0",
            "14 * 1024**3",
            "210 or available < 0.85",
            "Older native attempt exists",
        ):
            if token == "Older native attempt exists":
                self.assertIn("Earlier native attempt exists", self.source)
            elif token == "get_engine_version":
                self.assertIn("PatchVersion", self.source)
            else:
                self.assertIn(token, self.source)

    def test_editor_other_process_and_protected_content(self):
        for token in (
            "unrealeditor.exe", "unrealeditor-cmd.exe", "livecodingconsole.exe",
            "Saved/SaveGames", "os.chmod(f, stat.S_IREAD)",
            "os.chmod(f, stat.S_IWRITE | stat.S_IREAD)",
            "config_shas_preserved", "base_map_sha_preserved",
            "source_head_preserved", "status", "NATIVE_ASSET_STAGE_HOLD",
            "TSTSS_FIRST_WAKE_ASSET_ASSEMBLY_NATIVE_SAVE_RELOAD_PASS",
        ):
            self.assertIn(token, self.source)
        self.assertNotIn("taskkill", self.source)
        self.assertNotIn("rm -rf", self.source)

    def test_nullrhi_not_pie_or_approval(self):
        for token in ('"-NullRHI"', '"pie_verified": False', '"gpu_rendered": False',
                      '"production_art_approved": False', '"starbourne_unlocked": False',
                      '"NATIVE_ASSET_WORLD_SAVED_RELOADED_NOT_PIE"'):
            self.assertIn(token, self.source)


if __name__ == "__main__":
    unittest.main()
