"""Source-only safeguards for optional native First Wake asset review launcher."""
import re
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).with_name("Start-FirstWakeAssetReview.ps1")


class AssetEditorLauncherContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = LAUNCHER.read_text(encoding="utf-8")

    def test_exact_workspace_and_commit_custody(self):
        for token in (
            "TSTSS_AssetAssembly_20261104", "ExpectedHead",
            "status --porcelain --untracked-files=no",
            "merge-base --is-ancestor", "be9bc0e42d3cdf4f52a5c6bc3bcc8273a0d7e94d",
            "gameplay/config/engine files changed after native stage",
            "unreal/Source", "unreal/Config",
        ):
            self.assertIn(token, self.source)

    def test_native_map_and_imported_asset_admission(self):
        for token in (
            "FirstWake_AssetAssembly_20261104_REVIEW_V3",
            "54b4e266683347fc950a56c8ac8691d99aaddb41d61e304ddf0f5b4d0730e2b5",
            "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80",
            "first_wake_asset_scene_readback_v3_20261104.json",
            "first_wake_asset_scene_native_v3_20261104.json",
            "host_asset_stage_v3_20261104.json",
            "INDEPENDENT_NATIVE_SAVED_WORLD_READBACK_PASS_NOT_PIE",
            "StageHost.native_asset_sha256.PSObject.Properties",
            "imported_asset_actor_count -ne 10",
            "milestone_count -ne 7",
        ):
            self.assertIn(token, self.source)

    def test_real_6point5_gib_graphical_gate(self):
        self.assertIn("(Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory", self.source)
        self.assertIn("if ($FreeKiB -lt 6815744)", self.source)
        for gib, refuse in ((6.20, True), (6.49, True), (6.50, False), (6.51, False)):
            with self.subTest(free_gib=gib):
                self.assertEqual(int(gib * 1024 * 1024) < 6815744, refuse)

    def test_editor_is_optin_and_all_files_restored(self):
        for marker in (
            "if (-not $OpenEditor) { return }",
            "Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole",
            "Saved/SaveGames", "14GB", "DefaultEngine.ini", "DefaultInput.ini",
            "IsReadOnly = $true", "IsReadOnly = $false",
            "Start-Process -FilePath $Editor", "$Process.WaitForExit()",
            "Get-Sha256 $Item.Path", "FIRST_WAKE_ASSET_REVIEW_PREFLIGHT_PASS",
        ):
            self.assertIn(marker, self.source)
        self.assertLess(
            self.source.index("if (-not $OpenEditor) { return }"),
            self.source.index("Start-Process -FilePath $Editor"),
        )
        for forbidden in ("Stop-Process", "taskkill", "Remove-Item",
                          "DeleteGameInSlot", "SaveGameToSlot",
                          "EditorAssetLibrary.duplicate_asset"):
            self.assertNotIn(forbidden, self.source)


if __name__ == "__main__":
    unittest.main()
