"""Source-only regression tests for the exact-head, non-destructive launcher."""
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
                     "FreePhysicalMemory -lt 5242880",
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
        self.assertIn("Get-FileHash",self.s)
        self.assertIn("source HEAD differs",self.s)
        self.assertIn("player_keyboard='NOT_VERIFIED'",self.s)
        self.assertIn("speaker_audio='NOT_VERIFIED'",self.s)
    def test_keys_are_only_centering_and_pulse(self):
        self.assertIn("1 = Centering",self.s)
        self.assertIn("2 = Resonant Pulse",self.s)
        self.assertNotIn("3 = Correspondence",self.s)
if __name__=="__main__":main()
