"""Fail-closed source contracts for optional Windows UE native Prelude launcher.

These tests NEVER invoke UBT/Editor or read user SaveGames. Windows and CI
PowerShell syntax/failure-path evidence is a separate gate.
"""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = ROOT / "Tools/Invoke-NativePreludeMapQA.ps1"
BUILDER = ROOT / "Tools/Verify-Unreal.ps1"
DOC = ROOT / "Docs/FIRST_WAKE_NATIVE_MAP_ADMISSION_2026-11-02.md"
WORKFLOW = ROOT.parent / ".github/workflows/unreal-source-preflight.yml"


def check_launcher(source: str, build_source: str) -> None:
    for marker in (
        "TSTSS_PR713_NativeMapQA_20261102",
        "TSTSS_PR735_NativeMapQA_20261103",
        "$AllowedReviewRoots",
        "-notin $AllowedReviewRoots",
        "ExpectedHead must be a full 40-character Git SHA",
        "'Engine/Build/Build.version'",
        "function Get-TSTSSSha256",
        "[System.Security.Cryptography.SHA256]::Create()",
        "[System.IO.File]::OpenRead($Path)",
        "$FileStream.Dispose()",
        "$Hasher.Dispose()",
        "Get-TSTSSSha256 -Path $MapPath",
        "status --porcelain",
        "Saved/SaveGames",
        "HOLD: isolated review workspace contains SaveGame files",
        "DefaultEngine.ini",
        "DefaultInput.ini",
        "must be write-protected before Editor execution",
        "Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole'",
        "HOLD: active Unreal Editor or Live Coding session",
        "if ($PreflightOnly)",
        "NATIVE_PRELUDE_MAP_PREFLIGHT_PASS_NO_EDITOR_LAUNCHED",
        "verified-build.json",
        "WIN64_EDITOR_BUILD_PASS_CLEAN_SOURCE",
        "no exact-SHA verified build-only success receipt",
        "TSTSS_REVIEW_EXPECTED_HEAD",
        "UnrealEditor-Cmd.exe",
        "'-run=pythonscript'",
        "TSTSS_NATIVE_PRELUDE_MAP_QA_PASS",
        "Assert-NativePreludeMapReceipt.ps1",
        "Assert-TSTSSNativePreludeMapReceipt -Report $Payload",
        "NATIVE_EDITOR_MAP_RECEIPT_SCHEMA_ACCEPTED_NOT_PIE",
        "exactly one fresh, non-overwriting map-QA report",
        "P01_P13 -cne 'NOT_TESTED'",
        "WaterPhysics -cne 'NOT_AUTHORIZED'",
        "Release -cne 'NOT_AUTHORIZED'",
        "NativePreludeMapQA",
        "LauncherReceipts",
        "NATIVE_EDITOR_MAP_ACTORS_PASS_NOT_PIE",
        "PIE_P01_P13=NOT_TESTED",
    ):
        if marker not in source:
            raise ValueError("Native map QA launcher missing safety requirement: " + marker)
    if not (source.index("status --porcelain") <
            source.index("Saved/SaveGames") <
            source.index("Get-Process -Name 'UnrealEditor'") <
            source.index("if ($PreflightOnly)") <
            source.index("verified-build.json") <
            source.index("New-Item -Path $LauncherRoot")):
        raise ValueError("Native map QA launcher launches or creates reports before preflight holds")
    for token in (
        "WIN64_EDITOR_BUILD_PASS_CLEAN_SOURCE",
        "verified-build.json",
        "source_sha = $GitHead",
        "native_automations = 'NOT_TESTED'",
        "Working tree changed during build; build-only evidence rejected",
    ):
        if token not in build_source:
            raise ValueError("Build verifier must not mint an unvalidated success receipt: " + token)
    if not (build_source.index("Working tree changed during build; build-only evidence rejected") <
            build_source.index("$BuildOnlyReceipt = [ordered]@{")):
        raise ValueError("Build receipt created before checking exact source custody")
    # No destructive operations on the saved report or player data. Removing
    # this process's temporary environment variable is harmless.
    for banned in (
        "DeleteGameInSlot", "delete_game_in_slot",
        "Remove-Item -LiteralPath $OutputRoot", "Remove-Item $SaveDir",
        "Remove-Item -Recurse", "save_map", "editor_request_begin_play",
        "Stop-Process", "taskkill", "Set-ItemProperty",
    ):
        if banned in source:
            raise ValueError("Unsafe native launcher operation: " + banned)


class LauncherContractTests(unittest.TestCase):
    def setUp(self):
        self.launcher = LAUNCHER.read_text(encoding="utf-8")
        self.build = BUILDER.read_text(encoding="utf-8")

    def check_failed(self, altered: str, expected: str):
        with self.assertRaisesRegex(ValueError, expected):
            check_launcher(altered, self.build)

    def test_current_scripts_hold_safe_boundaries(self):
        check_launcher(self.launcher, self.build)

    def test_joined_root_is_narrow_and_cannot_disable_root_check(self):
        self.assertIn("-notin $AllowedReviewRoots", self.launcher)
        self.assertIn("TSTSS_PR735_NativeMapQA_20261103", self.launcher)
        self.check_failed(self.launcher.replace(
            "TSTSS_PR735_NativeMapQA_20261103", "ANY_WORKTREE"),
            "TSTSS_PR735_NativeMapQA_20261103")

    def test_sha256_has_no_missing_windows_cmdlet_dependency(self):
        self.assertNotIn("(Get-FileHash -LiteralPath", self.launcher)
        self.assertIn("[System.Security.Cryptography.SHA256]::Create()", self.launcher)

    def test_sha_hasher_mutation_rejected(self):
        self.check_failed(
            self.launcher.replace("[System.Security.Cryptography.SHA256]::Create()",
                                  "[System.Security.Cryptography.MD5]::Create()"),
            "SHA256",
        )

    def test_no_active_editor_guard_mutation(self):
        self.check_failed(
            self.launcher.replace("Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole'",
                                  "Get-Process -Name 'OtherApp'"),
            "Get-Process",
        )

    def test_savegame_protection_cannot_be_removed(self):
        self.check_failed(
            self.launcher.replace(
                "HOLD: isolated review workspace contains SaveGame files",
                "Ignore existing review SaveGames"),
            "SaveGame",
        )

    def test_reject_missing_verified_build_receipt(self):
        self.check_failed(
            self.launcher.replace("verified-build.json", "legacy_build_log.txt"),
            "verified-build.json",
        )

    def test_no_fabricated_pie_success(self):
        self.check_failed(
            self.launcher.replace("PIE_P01_P13=NOT_TESTED", "PIE_P01_P13=PASS"),
            "PIE_P01_P13=NOT_TESTED",
        )

    def test_independent_report_schema_gate_cannot_be_removed(self):
        self.check_failed(
            self.launcher.replace("Assert-TSTSSNativePreludeMapReceipt -Report $Payload",
                                  "Write-Host 'assume all seven passed'"),
            "Assert-TSTSSNativePreludeMapReceipt",
        )

    def test_schema_validator_and_fixture_runner_are_wired(self):
        validator = (ROOT / "Tools/Assert-NativePreludeMapReceipt.ps1").read_text(encoding="utf-8")
        fixtures = (ROOT / "Tools/Test-NativePreludeMapReceiptFixtures.ps1").read_text(encoding="utf-8")
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("function Assert-TSTSSNativePreludeMapReceipt", validator)
        self.assertIn("actual_reflected_game_mode_pawn_present", validator)
        self.assertIn("character_or_ship_art_approved", validator)
        self.assertIn("UNSAFE_MAP_REPORT_ACCEPTED", fixtures)
        self.assertIn("Test-NativePreludeMapReceiptFixtures.ps1", workflow)

    def test_no_force_kill_reviewer_editor(self):
        self.check_failed(self.launcher + "\nStop-Process -Name UnrealEditor -Force\n",
                          "Unsafe native launcher")

    def test_no_automatic_removal_of_player_saves(self):
        self.check_failed(self.launcher + "\nRemove-Item $SaveDir -Recurse -Force\n",
                          "Unsafe native launcher")

    def test_builder_receipt_must_wait_for_clean_tree(self):
        changed = self.build.replace("Working tree changed during build; build-only evidence rejected",
                                     "Skip git status after build")
        with self.assertRaisesRegex(ValueError, "Build verifier"):
            check_launcher(self.launcher, changed)

    def test_ci_parses_launcher_and_checks_its_contract(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("Invoke-NativePreludeMapQA.ps1", workflow)
        self.assertIn("test_native_prelude_launcher.py", workflow)

    def test_docs_explicitly_keep_native_pie_hold(self):
        doc = DOC.read_text(encoding="utf-8")
        self.assertIn("Invoke-NativePreludeMapQA.ps1", doc)
        self.assertIn("P01–P13", doc)
        self.assertIn("verified-build.json", doc)


if __name__ == "__main__":
    unittest.main()
