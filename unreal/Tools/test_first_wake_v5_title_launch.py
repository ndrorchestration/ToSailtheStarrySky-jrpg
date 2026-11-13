"""Engine-free checks for the opt-in V5 title -> real Prelude -> ship review launcher.

Do not infer a UE build, audio playback, runtime traversal or visual approval.
"""
from pathlib import Path
import hashlib
import re
import shutil
import subprocess
import tempfile
import unittest

UNREAL = Path(__file__).resolve().parents[1]
SCRIPT = UNREAL / "Tools/Launch-TSTSS-V5FirstWakeJourney.ps1"
WIDGET = UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSOpeningReviewWidget.cpp"
MODE = UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSOpeningReviewMode.cpp"
GAME = UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSGameMode.cpp"
CONFIG = UNREAL / "Config/DefaultEngine.ini"


class FirstWakeV5TitleLauncherSource(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.widget = WIDGET.read_text(encoding="utf-8")
        cls.mode = MODE.read_text(encoding="utf-8")
        cls.game = GAME.read_text(encoding="utf-8")

    def test_real_title_and_native_v5_player_route(self):
        s = self.script
        for part in (
            "Opening\\L_FirstWake_TitleReview.umap",
            "FirstWake_PreludeInteraction_V5_VisualReview.umap",
            "VerticalSlice\\VS02_AureateInteriors.umap",
            "VerticalSlice\\VS03_FirstWakeSky.umap",
            "VerticalSlice\\VS04_SplashdownSea.umap",
            "VerticalSlice\\VS05_DenithFuelShanty.umap",
            "MultipathV1\\L_VS06_ShoreMagicEnemyGear_Review.umap",
        ):
            self.assertIn(part, s)
            self.assertTrue(
                (UNREAL / "Content/TSTSS/Review" / part.replace("\\", "/")).is_file(),
                f"Missing tracked world asset: {part}",
            )
        self.assertIn("$TitlePackage + '?game=' + $TitleMode", s)
        self.assertIn("/Script/ToSailTheStarrySky.TSTSSOpeningReviewMode", s)
        self.assertIn("UGameplayStatics::OpenLevel(Controller, FName(*PreludeMap))",
                      self.widget)
        self.assertIn(
            '/Game/TSTSS/Review/FirstWake_PreludeInteraction_V5_VisualReview',
            self.widget,
        )
        self.assertIn("DefaultPawnClass = ASpectatorPawn::StaticClass()", self.mode)
        self.assertIn("DefaultPawnClass = ATSTSSExplorerCharacter::StaticClass()", self.game)
        self.assertIn(
            "GlobalDefaultGameMode=/Script/ToSailTheStarrySky.TSTSSGameMode",
            CONFIG.read_text(encoding="utf-8"),
        )
        self.assertNotIn("'VerticalSlice\\VS01_DenithHarbor.umap'", s)

    def test_strict_host_and_source_boundary_before_native_spawn(self):
        s = self.script
        markers = (
            "Git-Read -GitArgs @('branch','--show-current')",
            "$Branch.StartsWith('review/')",
            "Git-Read -GitArgs @('status','--porcelain','-uall')",
            "Get-CimInstance Win32_OperatingSystem",
            "6815744",
            "(14 * 1GB)",
            "Get-Process -Name 'UnrealEditor','UnrealEditor-Cmd','LiveCodingConsole'",
            "Get-CimInstance Win32_Process",
            "OtherBuilds.Count -gt 0",
            "Start-Process -FilePath $Editor",
        )
        for marker in markers:
            self.assertIn(marker, s)
        self.assertLess(s.index("Git-Read -GitArgs @('status','--porcelain','-uall')"),
                        s.index("Start-Process -FilePath $Editor"))
        self.assertLess(s.index("$OtherEditors ="), s.index("Start-Process -FilePath $Editor"))
        self.assertLess(s.index("$OtherBuilds ="), s.index("Start-Process -FilePath $Editor"))
        self.assertLess(s.index("$NativeAccepted = $false"),
                        s.index("Start-Process -FilePath $Editor"))
        self.assertLess(s.index("if ($PrintOnly)"), s.index("$NativeAccepted = $false"))
        self.assertIn("if (-not $NativeAccepted)", s)

    def test_full_same_head_native_38_receipt_required_without_weakening_gates(self):
        s = self.script
        self.assertIn("verified-native.json", s)
        self.assertIn("Assert-TSTSSNativeAutomationReport", s)
        self.assertIn("Assert-NativeAutomationReport.ps1", s)
        self.assertIn("$Names.Count -ne 38", s)
        self.assertIn("$Receipt.required_native_tests -ne 38", s)
        self.assertIn("$Receipt.source_sha -ine $Head", s)
        self.assertIn("(Get-Content -LiteralPath $HeadPath -Raw).Trim() -ine $Head", s)
        self.assertIn("(Get-TSTSSReviewSHA256 -LiteralPath $ReportPath)", s)
        self.assertIn("[System.Security.Cryptography.SHA256]::Create()", s)
        self.assertIn("[System.IO.File]::Open($Resolved", s)
        self.assertNotIn("Get-FileHash -LiteralPath $ReportPath", s)
        self.assertIn("$Receipt.visual_approval -ne 'NOT_TESTED'", s)
        self.assertIn("HOLD: no matching full 38-test native receipt at this source HEAD", s)
        self.assertNotIn("SkipTests", s)
        self.assertNotIn("Override", s)
        self.assertNotIn("Force", s)

    def test_receipt_hash_independent_of_cmdlet_and_rejects_tampering(self):
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell unavailable for SHA-256 executable fixture")
        match = re.search(
            r"(?s)(function Get-TSTSSReviewSHA256\(\[string\]\$LiteralPath\) \{.*?\n\})\s*\$Repo =",
            self.script,
        )
        self.assertIsNotNone(match, "Real launcher hash helper not found")
        with tempfile.TemporaryDirectory() as temp:
            sample = Path(temp) / "synthetic-report.json"
            sample.write_bytes(b'{"tests":[],"synthetic":true}')
            expected = hashlib.sha256(sample.read_bytes()).hexdigest()
            quoted = str(sample).replace("'", "''")
            fixture = Path(temp) / "verify-hash.ps1"
            fixture.write_text(
                "$ErrorActionPreference = 'Stop'\n"
                + match.group(1) + "\n"
                + "$original = Get-TSTSSReviewSHA256 -LiteralPath '" + quoted + "'\n"
                + "if ($original -cne '" + expected + "') { exit 11 }\n"
                + "[System.IO.File]::AppendAllText('" + quoted + "', 'TAMPER')\n"
                + "$modified = Get-TSTSSReviewSHA256 -LiteralPath '" + quoted + "'\n"
                + "if ($modified -ceq '" + expected + "') { exit 12 }\n"
                + "Write-Output 'HASH_FIXTURE_PASS'\n",
                encoding="utf-8",
            )
            result = subprocess.run(
                [shell, "-NoProfile", "-NonInteractive", "-File", str(fixture)],
                capture_output=True, text=True, timeout=30, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("HASH_FIXTURE_PASS", result.stdout)

    def test_launcher_does_not_write_save_or_stage_assets(self):
        s = self.script
        for forbidden in (
            "Remove-Item", "Stop-Process", "taskkill", "git checkout",
            "git reset", "git merge", "SaveGameToSlot", "Set-Content",
            "Copy-Item", "Move-Item", "UnrealEditor-Cmd.exe",
            "-ExecutePythonScript", "-run=pythonscript", "-NoSound",
        ):
            self.assertNotIn(forbidden, s)
        self.assertEqual(s.count("Start-Process -FilePath $Editor"), 1)

    def test_powershell_parser_if_available(self):
        pwsh = shutil.which("pwsh")
        if not pwsh:
            self.skipTest("PowerShell 7 unavailable; source contract still tested")
        cmd = (
            "$tokens=$null;$parseErrors=$null;"
            "[System.Management.Automation.Language.Parser]::ParseFile("
            "'" + str(SCRIPT).replace("'", "''") + "',"
            "[ref]$tokens,[ref]$parseErrors) | Out-Null;"
            "if ($parseErrors.Count -gt 0) {"
            "$parseErrors | ForEach-Object { Write-Error $_.Message }; exit 1"
            "}"
        )
        completed = subprocess.run(
            [pwsh, "-NoProfile", "-NonInteractive", "-Command", cmd],
            text=True, capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(completed.returncode, 0,
                         (completed.stdout + completed.stderr)[-4000:])


if __name__ == "__main__":
    unittest.main()
