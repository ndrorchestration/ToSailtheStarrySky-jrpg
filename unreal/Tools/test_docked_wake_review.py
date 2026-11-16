"""Source integration checks only; native player-input proof is separate."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPLORER = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")

class DockedWakeReviewTests(unittest.TestCase):
    def test_shipboard_signoff_beacons_are_updated_from_live_state(self):
        tick = EXPLORER.split("void ATSTSSExplorerCharacter::Tick(", 1)[1].split("void ATSTSSExplorerCharacter::", 1)[0]
        gate = tick.split("It->UpdateReviewBeacon(FirstWakeState)", 1)[0]
        self.assertIn('Scene == TEXT("VS02_AureateInteriors")', gate)

    def test_earned_ship_target_opens_interior(self):
        interaction = EXPLORER.split("void ATSTSSExplorerCharacter::Interact()", 1)[1].split("void ATSTSSExplorerCharacter::", 1)[0]
        accepted = interaction.split("if (Milestone->TryActivate(FirstWakeState))", 1)[1].split("else", 1)[0]
        self.assertIn('TEXT("TSTSS_PRELUDE_REVIEW_AureateBoarding")', accepted)
        self.assertIn("ReviewShoreTravel();", accepted)

    def test_captain_visual_has_explicit_world_placement_after_root_registration(self):
        stage = EXPLORER.split("void StageDockedWakeReview(", 1)[1].split(
            "void StageEarnedEngineRoomReview(", 1)[0]
        self.assertIn("CaptainVisual->SetActorLocation(", stage)
        self.assertGreater(stage.index("CaptainVisual->SetActorLocation("),
                           stage.index("Root->RegisterComponent()"))
        self.assertIn('CaptainVisual->SetActorLocation(FVector(-1250.f, 200.f, 0.f))', stage)

    def test_docked_ship_and_captain_markers_are_staged_in_v5_only(self):
        self.assertIn("StageDockedWakeReview(GetWorld())", EXPLORER)
        self.assertIn("TSTSS_DOCKED_WAKE_REVIEW_APPLIED", EXPLORER)
        self.assertIn("AAureateWakePreviewActor::StaticClass()", EXPLORER)

if __name__ == "__main__":
    unittest.main()
