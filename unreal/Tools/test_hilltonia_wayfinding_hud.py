"""Review-only wayfinding contract: distinguish walking from [E] interactions.

Source checks do not establish Unreal/PIE visual quality or real traversal.
The actual DrawHUD behavior is separately compiled with C++ API doubles by
check_first_wake_review_hud_compiled.py.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HUD = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSFirstWakeReviewHUD.cpp"
       ).read_text(encoding="utf-8")
HARNESS = (ROOT / "Tools/check_first_wake_review_hud_compiled.py"
           ).read_text(encoding="utf-8")
ROUTE = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSHilltoniaRouteTelemetry.h"
         ).read_text(encoding="utf-8")


class HilltoniaReviewWayfindingTests(unittest.TestCase):
    def test_only_authorized_standalone_v5_game_map(self):
        for token in (
            '#if !UE_BUILD_SHIPPING',
            'FirstWake_PreludeInteraction_V5_VisualReview',
            'World->WorldType == EWorldType::PIE',
            'World->WorldType == EWorldType::Game',
            'World->GetNetMode() == NM_Standalone',
            'Canvas->ClipX >= 1260.f',
            'Canvas->ClipY >= 500.f',
        ):
            self.assertIn(token, HUD)
        self.assertIn('unrelated world must not receive Hilltonia panel', HARNESS)
        self.assertIn('network worlds must not show local review wayfinding', HARNESS)
        self.assertIn('shipping build must never show debug review overlay', HARNESS)

    def test_legible_exploration_without_fake_e_target(self):
        for token in (
            "HILLTONIA  |  EXPLORATION ROUTE",
            "ROAD  |  WEST: HILLTONIA / EAST: HARBOR",
            "VILLAGE SQUARE  |  WEST END / INLAND FOREST",
            "TOWN WEST END  |  EAST: SQUARE",
            "FOREST PATH  |  INLAND: EDGE / BACK: TOWN",
            "FOREST EDGE  |  BACK: VILLAGE SQUARE",
            "Scenery is NOT an [E] quest target",
            "WASD: walk",
            "FOLLOW THE GOLD MARKER",
            "Explorer->GetReviewAimStatus()",
        ):
            self.assertIn(token, HUD)
        self.assertIn("distinguish non-interactive roads from E markers", HARNESS)
        self.assertIn("forest branch must explain how to return to town", HARNESS)
        self.assertIn("west-end arrival must direct the return", HARNESS)
        self.assertIn("forest edge must direct the return", HARNESS)
        self.assertIn("wayfinding reads geography; it must never mutate story state", HARNESS)

    def test_position_guard_does_not_mutate_gameplay(self):
        for token in (
            "const FVector Position = Explorer->GetActorLocation();",
            "Position.ContainsNaN()",
            "FMath::IsFinite(Position.X)",
            "FMath::IsFinite(Position.Y)",
            "FMath::IsFinite(Position.Z)",
            "Position.X <= -2800.f && Position.X >= -9700.f",
            "Position.Y >= -3650.f && Position.Y <= 1200.f",
        ):
            self.assertIn(token, HUD)
        self.assertIn("nonfinite pawn positions must not generate navigation labels", HARNESS)
        self.assertIn("narrow view must not clip an overlapping Hilltonia side panel", HARNESS)
        for forbidden in (
            "AdvanceTo(", "TryActivate(", "OpenLevel(", "SetActorLocation(",
            "TeleportTo(", "SaveGameToSlot(", "SaveLoadedAsset(", "SetMaterial(",
        ):
            self.assertNotIn(forbidden, HUD)

    def test_waypoints_remain_separate_observational_contract(self):
        self.assertIn('TEXT("FOREST_EDGE")', ROUTE)
        self.assertIn('TEXT("TOWN_WEST_END")', ROUTE)
        self.assertIn("No controller commands, teleport, quest authority", ROUTE)
        self.assertIn("review-only interaction prompt", HUD)
        self.assertIn("road and forest track from the gold [E]", HUD)


if __name__ == "__main__":
    unittest.main()
