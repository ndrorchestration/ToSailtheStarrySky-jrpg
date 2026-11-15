"""Source-only failure guards for isolated three-foe focus review startup.

These tests cannot certify Unreal UHT/UBT, runtime PIE, input, sound or GPU.
"""
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
CPP = (
    HERE.parent
    / "Source/ToSailTheStarrySky/Private/Review/TSTSSResonatorFocusReviewActor.cpp"
)
HEADER = (
    HERE.parent
    / "Source/ToSailTheStarrySky/Public/Review/TSTSSResonatorFocusReviewActor.h"
)
LAUNCH = HERE / "Start-EnderResonatorFocusReview.ps1"


def enforce(code: str, header: str, launcher: str) -> None:
    if "bool bMultiEnemyPulseProofReview=false;" not in header:
        raise ValueError("Default-off three-foe source gate missing")
    start = code.split(
        "void ATSTSSResonatorFocusReviewActor::BeginPlay()", 1
    )[-1].split("void ATSTSSResonatorFocusReviewActor::TryAttachReviewPlayer()", 1)[0]
    required_cpp = (
        "!bEnableFocusReview || !ActorHasTag(TEXT(\"TSTSSReviewOnly\"))",
        "!GetWorld()->IsGameWorld()",
        "#if WITH_EDITOR",
        'FParse::Param(FCommandLine::Get(), TEXT("TSTSSFocusMultiProbe"))',
        'MapName.EndsWith(TEXT("L_EnderCenteringPulseReview_V2"))',
        'TEXT("TSTSS_FOCUS_MULTIFOE_CLI_DENIED: wrong review map")',
        "bMultiEnemyPulseProofReview=true;",
        'TEXT("TSTSS_FOCUS_MULTIFOE_CLI_OPTIN: V2 map review only")',
    )
    for token in required_cpp:
        if token not in start:
            raise ValueError("C++ review opt-in gate missing: " + token)
    if start.index("!bEnableFocusReview") > start.index("FParse::Param("):
        raise ValueError("Map CLI flag applied before actor authorization")
    if start.index("MapName.EndsWith(") > start.index("bMultiEnemyPulseProofReview=true"):
        raise ValueError("Multi-foe enabled before exact review map gate")
    required_launcher = (
        "[switch]$MultiEnemyProof",
        "$MultiProbeReview=$WorktreeName -eq 'TSTSS_840_PulseReadback_20261115'",
        "($MultiEnemyProof -and -not $MultiProbeReview)",
        "if ($MultiEnemyProof)",
        "$Map='/Game/TSTSS/Review/ResonatorFocus/L_EnderCenteringPulseReview_V2'",
        "$PinnedBlob=(git -C $Root rev-parse",
        "$ActualBlob=(git -C $Root hash-object",
        "$PinnedBlob -ne $ActualBlob",
        "$Parameters+= '-TSTSSFocusMultiProbe'",
        "three_foe_hp_mp='NOT_VERIFIED'",
        "NO_EDITOR_LAUNCHED; NATIVE_PROCESS_RAM_PIE_GPU_AUDIO_NOT_TESTED",
        "$Memory.FreePhysicalMemory -lt 6815744",
        "$Disk.Free -lt 14GB",
        "another Unreal/LiveCoding session is active",
    )
    for token in required_launcher:
        if token not in launcher:
            raise ValueError("Launcher opt-in/custody gate missing: " + token)
    if launcher.index("$PinnedBlob=(git") > launcher.index("if ($CheckAssetsOnly)"):
        raise ValueError("Custody-only mode skips V2 exact-head map proof")
    if launcher.index("if ($CheckAssetsOnly)") > launcher.index("Get-Process UnrealEditor"):
        raise ValueError("Custody check starts native operations")
    if launcher.index("$PinnedBlob=(git") > launcher.index("Start-Process -FilePath"):
        raise ValueError("Native launch before V2 map integrity")
    for forbidden in ("Stop-Process", "Remove-Item", "git reset", "git clean"):
        if forbidden in launcher:
            raise ValueError("Destructive launcher operation: " + forbidden)


class ThreeFoeLaunchSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = CPP.read_text(encoding="utf-8")
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.launch = LAUNCH.read_text(encoding="utf-8")

    def test_exact_review_map_and_two_step_optin(self):
        enforce(self.cpp, self.header, self.launch)

    def test_default_on_mutation_denied(self):
        with self.assertRaisesRegex(ValueError, "Default-off"):
            enforce(self.cpp, self.header.replace(
                "bMultiEnemyPulseProofReview=false;",
                "bMultiEnemyPulseProofReview=true;"), self.launch)

    def test_missing_ue_editor_guard_denied(self):
        with self.assertRaisesRegex(ValueError, "C\\+\\+ review"):
            enforce(self.cpp.replace("#if WITH_EDITOR", "#if 1"),
                    self.header, self.launch)

    def test_no_exact_map_gate_denied(self):
        with self.assertRaisesRegex(ValueError, "C\\+\\+ review"):
            enforce(self.cpp.replace(
                'MapName.EndsWith(TEXT("L_EnderCenteringPulseReview_V2"))',
                "MapName.IsEmpty()"),
                self.header, self.launch)

    def test_launcher_cannot_choose_other_worktree(self):
        with self.assertRaisesRegex(ValueError, "Launcher opt-in"):
            enforce(self.cpp, self.header, self.launch.replace(
                "TSTSS_840_PulseReadback_20261115", "TSTSS_838_EngineRoomRoute_20261114"))

    def test_launcher_cannot_skip_map_hash(self):
        with self.assertRaisesRegex(ValueError, "Launcher opt-in"):
            enforce(self.cpp, self.header, self.launch.replace(
                "$PinnedBlob -ne $ActualBlob", "$PinnedBlob -eq $ActualBlob"))

    def test_launcher_cannot_claim_pie_accepted(self):
        with self.assertRaisesRegex(ValueError, "Launcher opt-in"):
            enforce(self.cpp, self.header, self.launch.replace(
                "three_foe_hp_mp='NOT_VERIFIED'",
                "three_foe_hp_mp='PASS'"))


if __name__ == "__main__":
    unittest.main()
