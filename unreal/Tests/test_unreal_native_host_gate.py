"""Verify that native UE automation cannot run before exact engine/toolchain checks."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOST = (ROOT / "Tools" / "Check-UnrealHost.ps1").read_text(encoding="utf-8")
VERIFY = (ROOT / "Tools" / "Verify-Unreal.ps1").read_text(encoding="utf-8")
TESTS = (ROOT / "Tests" / "Check-UnrealHost.Tests.ps1").read_text(encoding="utf-8")


class NativePreflightSourceTests(unittest.TestCase):
    def test_build_is_blocked_by_real_prerequisite_gate(self):
        self.assertIn("& $PrereqGate -EngineRoot $EngineRoot -RequireReady", VERIFY)
        self.assertIn("if ($LASTEXITCODE -ne 0)", VERIFY)
        self.assertLess(VERIFY.index("& $PrereqGate -EngineRoot"),
                        VERIFY.index("& $BuildTool ToSailTheStarrySkyEditor"))
        self.assertLess(VERIFY.index("& $PrereqGate -EngineRoot"),
                        VERIFY.index("& $EditorCmd $Project"))

    def test_readiness_checks_real_version_and_binary_not_dir_name(self):
        self.assertIn("Engine\\Build\\Build.version", HOST)
        self.assertIn("ConvertFrom-Json", HOST)
        self.assertIn("$Manifest.MajorVersion -eq 5", HOST)
        self.assertIn("$Manifest.MinorVersion -eq 8", HOST)
        self.assertIn("$Manifest.PatchVersion -ge $MinimumPatch", HOST)
        self.assertIn("[int]$MinimumPatch = 4", HOST)
        self.assertIn("$EngineVersionValid", HOST)
        self.assertIn("$UnrealValid", HOST)
        self.assertIn("$CxxValid", HOST)
        self.assertIn("$SdkValid", HOST)

    def test_explicit_success_and_rejection_exit_codes(self):
        self.assertIn("if ($RequireReady -and -not $Ready) { exit 2 }", HOST)
        self.assertTrue(HOST.rstrip().endswith("exit 0"))
        self.assertIn("ExpectedVersion = '5.8.4+'", HOST)

    def test_windows_regression_keeps_negative_and_positive_controls(self):
        for marker in ("old 5.7", "old 5.8.3", "current 5.8.4",
                       "future 5.8.6", "other 6.0", "invalid json",
                       "-RequireReady", "PASS: $Count"):
            self.assertIn(marker, TESTS)
        self.assertIn("Remove-Item -LiteralPath $Temp", TESTS)
        self.assertIn("$global:LASTEXITCODE = 0", TESTS)


if __name__ == "__main__":
    unittest.main()
