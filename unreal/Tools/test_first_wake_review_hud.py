"""Review HUD integration is bounded to the existing Prelude GameMode.

The C++ DrawHUD body is compiled/exercised separately with API doubles.
These source checks ensure that it is wired only in non-shipping targets,
keeps HUD source independent of title/class UI, and never mutates story/saves.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSGameMode.cpp"
HUD = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp"
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/TSTSSFirstWakeReviewHUD.h"
MODULE = ROOT / "Source/ToSailTheStarrySky/ToSailTheStarrySky.Build.cs"
WORKFLOW = ROOT.parent / ".github/workflows/unreal-source-preflight.yml"


class ObjectiveHudContracts(unittest.TestCase):
    def setUp(self):
        self.game = GAME.read_text(encoding="utf-8")
        self.hud = HUD.read_text(encoding="utf-8")
        self.header = HEADER.read_text(encoding="utf-8")

    def test_game_mode_wires_review_hud_only_nonshipping(self):
        self.assertIn('HUDClass = ATSTSSFirstWakeReviewHUD::StaticClass();', self.game)
        self.assertIn('DefaultPawnClass = ATSTSSExplorerCharacter::StaticClass();', self.game)
        self.assertLess(self.game.index('#if !UE_BUILD_SHIPPING'),
                        self.game.index('HUDClass = ATSTSSFirstWakeReviewHUD::StaticClass();'))
        self.assertLess(self.game.index('HUDClass = ATSTSSFirstWakeReviewHUD::StaticClass();'),
                        self.game.index('#endif'))

    def test_hud_reads_state_only_and_does_not_modify_story_or_saves(self):
        self.assertIn('GetFirstWakeState()', self.hud)
        self.assertIn('State->GetReviewObjectiveText()', self.hud)
        self.assertIn('PlayerOwner->GetPawn()', self.hud)
        self.assertIn('GetMediumFont()', self.hud)
        for forbidden in ("SaveFirstWake(", "LoadFirstWake(", "AdvanceTo(",
                          "InspectStation(", "Reset(", "Restore(", "SaveGameToSlot",
                          "SpawnActor(", "GetMutableDefault("):
            self.assertNotIn(forbidden, self.hud)
        self.assertIn('virtual void DrawHUD() override;', self.header)
        self.assertIn('UCLASS(NotBlueprintable)', self.header)

    def test_canvas_hud_stays_independent_of_class_umg(self):
        module = MODULE.read_text(encoding="utf-8")
        self.assertIn('"Engine", "InputCore"', module)
        for include in ('Slate/', 'SlateCore/', 'MediaPlayer.h', 'MediaTexture.h'):
            self.assertNotIn(include, self.hud)
            self.assertNotIn(include, self.header)
        self.assertNotIn('Blueprint/UserWidget.h', self.hud)
        self.assertNotIn('TSTSSJobSelectionReviewWidget', self.hud)
        self.assertIn('#include "Engine/Canvas.h"', self.hud)

    def test_review_ui_no_false_stage_or_shipping_claims(self):
        self.assertIn('#if !UE_BUILD_SHIPPING', self.hud)
        self.assertIn('PRELUDE REVIEW', self.hud)
        self.assertIn('no launch, water landing, or Chapter 1', self.hud)
        self.assertIn('PanelWidth < 440.f', self.hud)

    def test_ongoing_engineering_progress_uses_live_readonly_inspection_mask(self):
        self.assertIn('State->GetInspectionMask()', self.hud)
        self.assertIn('State->IsChapterOneActOne()', self.hud)
        for bit in ('0x01u', '0x02u', '0x04u'):
            self.assertIn('InspectionMask & ' + bit, self.hud)
        self.assertIn('const bool bCompact = PanelWidth < 640.f;', self.hud)
        self.assertIn('Systems: Lift / Pressure / Reserve', self.hud)
        self.assertIn('no sea landing or Chapter 1 approval', self.hud)

    def test_real_cplusplus_compiled_behavior_gate_is_in_ci(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn('check_first_wake_review_hud_compiled.py', workflow)
        self.assertIn('test_first_wake_review_hud.py', workflow)


if __name__ == "__main__":
    unittest.main()
