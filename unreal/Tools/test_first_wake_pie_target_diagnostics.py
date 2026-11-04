"""Engine-free contract for editor-only, one-press PIE interaction diagnostics.

These tests verify the diagnostics cannot grant progression, widen reach or
appear in production game builds. Runtime Unreal proof is a separate gate.
"""
from pathlib import Path
import unittest

SOURCE=(Path(__file__).resolve().parents[1]/
        "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp")


class EditorOnlyInteractionTelemetryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        src=SOURCE.read_text(encoding="utf-8")
        cls.interact=src.split("void ATSTSSExplorerCharacter::Interact()",1)[1].split(
            "void ATSTSSExplorerCharacter::ShowObjectiveReview()",1)[0]

    def test_success_and_rejection_are_both_visible(self):
        self.assertIn("TSTSS_PIE_REVIEW_E_ACCEPT target=%s",self.interact)
        self.assertIn("TSTSS_PIE_REVIEW_E_DENIED target=%s",self.interact)
        self.assertIn("pawn_hit_cm=%.1f",self.interact)
        self.assertIn("*Milestone->GetActorLabel()",self.interact)
        self.assertIn("*FirstWakeState->GetReviewObjectiveText()",self.interact)

    def test_only_in_editor_pie_and_no_extra_mutation(self):
        self.assertEqual(self.interact.count("#if WITH_EDITOR"),2)
        self.assertEqual(self.interact.count("#endif"),2)
        self.assertEqual(self.interact.count("GetWorld()->WorldType == EWorldType::PIE"),2)
        self.assertEqual(self.interact.count("Milestone->TryActivate(FirstWakeState)"),1)
        self.assertEqual(self.interact.count("ShowFirstWakeReviewObjective(FirstWakeState)"),1)
        self.assertEqual(self.interact.count("ShowFirstWakeReviewBlockedInteraction(FirstWakeState)"),1)
        self.assertEqual(self.interact.count("UE_LOG("),2)
        for forbidden in ("SetActorLocation(", "SetActorRotation(", "SaveGameToSlot(",
                          "OnMilestoneActivated(", "AdvanceTo(", "InteractionDistance ="):
            self.assertNotIn(forbidden,self.interact)

    def test_source_keeps_both_camera_and_pawn_reach_guards(self):
        self.assertIn("LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Query)",self.interact)
        self.assertIn("TSTSSInteractionReach::IsInsidePlayerReach(",self.interact)
        self.assertIn("TSTSSInteractionReach::GetCameraTraceLength(",self.interact)
        self.assertLess(self.interact.index("IsInsidePlayerReach("),
                        self.interact.index("TSTSS_PIE_REVIEW_E_ACCEPT"))

if __name__=="__main__":
    unittest.main()
