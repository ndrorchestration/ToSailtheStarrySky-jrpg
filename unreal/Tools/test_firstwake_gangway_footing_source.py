"""Source-only guard for V5 disposable gangway collision admission.

Does not prove native collision, grounded movement, or a human playthrough.
"""
import unittest
from pathlib import Path

UNREAL = Path(__file__).resolve().parents[1]
SOURCE = (UNREAL / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
AUTHOR = (UNREAL / "Tools/build_first_wake_prelude_interaction.py").read_text(encoding="utf8")
STAGE = SOURCE.split("void StageDockedWakeReview(UWorld* World)", 1)[1].split(
    "void StageEarnedEngineRoomReview(", 1
)[0]
BRIDGE = STAGE.split("// V5-only: turn the saved, deliberately non-colliding gangway", 1)[1].split(
    "Captain->Tags.AddUnique(", 1
)[0]


class DockedGangwaySourceContract(unittest.TestCase):
    def test_existing_authored_floor_stops_before_boarding_target(self):
        self.assertIn("FLOOR_LOCATION = (-600.0, 0.0, -100.0)", AUTHOR)
        self.assertIn("FLOOR_SCALE = (63.0, 14.0, 2.0)", AUTHOR)
        self.assertIn('("GangwayVisualMarker", (-1050, 800, 35), (6, 3, .7))', AUTHOR)
        self.assertIn('Board->SetActorLocation(FVector(-900.f, 790.f, 90.f))', STAGE)

    def test_review_only_and_one_existing_visual_marker(self):
        for token in (
            "World->WorldType != EWorldType::PIE",
            "World->GetNetMode() != NM_Standalone",
            'StartsWith(TEXT("/Game/TSTSS/Review/"))',
            'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            'GetActorLabel() == TEXT("TSTSS_PRELUDE_REVIEW_GangwayVisualMarker")',
            "GangwayCount != 1",
            "GetStaticMeshComponent()",
            "GetActorScale3D().Equals(FVector(6.f, 3.f, .7f), .02f)",
        ):
            self.assertIn(token, STAGE)

    def test_runtime_surface_is_grounded_and_not_a_trace_only_promise(self):
        for token in (
            "GangwayDeck->SetMobility(EComponentMobility::Movable)",
            "FVector(-1050.f, 750.f, -35.f)",
            "GangwayVisual->SetActorEnableCollision(true)",
            'GangwayDeck->SetCollisionProfileName(TEXT("BlockAll"))',
            "GangwayDeck->SetCollisionObjectType(ECC_WorldStatic)",
            "GangwayDeck->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics)",
            "GangwayDeck->SetGenerateOverlapEvents(false)",
            "top_z=0 y_min=600 y_max=900 collision=WorldStatic source_map_unchanged=1",
        ):
            self.assertIn(token, BRIDGE)
        self.assertIn("runtime_position_failed", BRIDGE)
        self.assertIn("missing_or_changed_review_marker", BRIDGE)

    def test_no_new_authority_or_map_save_in_gangway_repair(self):
        for token in (
            "AdvanceTo(", "TryActivate(", "SaveGameToSlot(", "OpenLevel(",
            "RequestForm(", "SnapToForm(", "SavePackage(", "LoadGameFromSlot(",
            "SetDefaultGameMode(", "SetActorEnableCollision(false)"
        ):
            self.assertNotIn(token, BRIDGE)
        self.assertNotIn("SpawnActor<", BRIDGE)
        self.assertNotIn("SetActorScale3D(", BRIDGE)


if __name__ == "__main__":
    unittest.main()