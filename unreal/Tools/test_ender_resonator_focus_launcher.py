"""Source-only regression tests for the exact-head, non-destructive launcher."""
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase,main
import verify_ender_resonator_focus_native as native

FILE=Path(__file__).with_name("Start-EnderResonatorFocusReview.ps1")

class LauncherSourceTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=FILE.read_text(encoding="utf8")
    def test_does_not_kill_or_modify_foreign_editor_processes(self):
        for term in ("[CmdletBinding()]","ExpectedHead",
                     "Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole",
                     "another Unreal/LiveCoding session is active",
                     "FreePhysicalMemory -lt 6815744",
                     "Disk.Free -lt 14GB",
                     "Start-Process -FilePath $Executable"):
            self.assertIn(term,self.s)
        for prohibited in ("Stop-Process","Remove-Item","git reset",
                           "git clean","git push","SaveGameToSlot"):
            self.assertNotIn(prohibited,self.s)
    def test_asset_hashes_and_exact_two_spell_admission(self):
        m=native.verify_sources()
        self.assertIn(m["map_package"],self.s)
        self.assertIn("DesignOnly / Correspondence ON HOLD",self.s)
        self.assertIn("merge-base --is-ancestor",self.s)
        self.assertIn("(Get-TSTSSFocusSHA256 -LiteralPath $Path)",self.s)
        self.assertIn("[System.Security.Cryptography.SHA256]::Create()",self.s)
        self.assertNotIn("Get-FileHash -LiteralPath $Path",self.s)
        self.assertIn("source HEAD differs",self.s)
        self.assertIn("player_keyboard='NOT_VERIFIED'",self.s)
        self.assertIn("speaker_audio='NOT_VERIFIED'",self.s)
    def test_executable_sha256_fixture_fails_when_asset_is_tampered(self):
        shell=shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell absent; source-only hash contract still checked")
        match=re.search(
            r"(?s)(function Get-TSTSSFocusSHA256\(\[string\]\$LiteralPath\) \{.*?\n\})\s*\$Root=",
            self.s)
        self.assertIsNotNone(match,"Real launcher SHA-256 helper missing")
        with tempfile.TemporaryDirectory() as tmp:
            asset=Path(tmp)/"pinned-review-asset.bin"
            asset.write_bytes(b"Review-only source asset; no Unreal game was launched")
            digest=hashlib.sha256(asset.read_bytes()).hexdigest()
            quoted=str(asset).replace("'","''")
            fixture=Path(tmp)/"verify-focus-hash.ps1"
            fixture.write_text(
                "$ErrorActionPreference='Stop'\n"+match.group(1)+"\n"+
                "$original=Get-TSTSSFocusSHA256 -LiteralPath '"+quoted+"'\n"+
                "if ($original -cne '"+digest+"') { exit 11 }\n"+
                "[System.IO.File]::AppendAllText('"+quoted+"','TAMPER')\n"+
                "$changed=Get-TSTSSFocusSHA256 -LiteralPath '"+quoted+"'\n"+
                "if ($changed -ceq '"+digest+"') { exit 12 }\n"+
                "Write-Output 'FOCUS_HASH_TAMPER_TEST_PASS'\n",
                encoding="utf8")
            result=subprocess.run(
                [shell,"-NoProfile","-NonInteractive","-File",str(fixture)],
                capture_output=True,text=True,timeout=30,check=False)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            self.assertIn("FOCUS_HASH_TAMPER_TEST_PASS",result.stdout)

    def test_joined_review_requires_explicit_opt_in_without_relaxing_native_gates(self):
        self.assertIn("[switch]$IntegratedReview", self.s)
        self.assertIn("[switch]$CheckAssetsOnly", self.s)
        self.assertIn("$WorktreeName -eq 'TSTSS_CenteringPulse_20261111'", self.s)
        self.assertIn("$WorktreeName -eq 'TSTSS_838_EngineRoomRoute_20261114'", self.s)
        self.assertIn("($JoinedReview -or $MultiProbeReview) -and $IntegratedReview", self.s)
        self.assertIn("missing explicit integration/multi-foe opt-in", self.s)
        self.assertIn("TSTSS_FOCUS_ASSET_CUSTODY_PASS", self.s)
        self.assertIn("NO_EDITOR_LAUNCHED; NATIVE_PROCESS_RAM_PIE_GPU_AUDIO_NOT_TESTED", self.s)
        # Asset audit must conclude after every immutable asset check,
        # but before it could reach any native runtime operation.
        self.assertLess(self.s.index("Get-TSTSSFocusSHA256 -LiteralPath $Path"),
                        self.s.index("if ($CheckAssetsOnly)"))
        self.assertLess(self.s.index("if ($CheckAssetsOnly)"),
                        self.s.index("Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole"))
        self.assertLess(self.s.index("Get-Process UnrealEditor,UnrealEditor-Cmd,LiveCodingConsole"),
                        self.s.index("Start-Process -FilePath $Executable"))
        self.assertIn("git -C $Root status --porcelain -uall", self.s)
        self.assertIn("merge-base --is-ancestor", self.s)

    def test_keys_are_only_centering_and_pulse(self):
        self.assertIn("1 = Centering",self.s)
        self.assertIn("2 = Resonant Pulse",self.s)
        self.assertNotIn("3 = Correspondence",self.s)
if __name__=="__main__":main()
