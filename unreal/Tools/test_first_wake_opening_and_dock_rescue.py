"""Source-contract regression checks; these do not establish native Unreal/PIE behavior."""
import unittest
from pathlib import Path

UNREAL = Path(__file__).resolve().parents[1]
SRC = UNREAL / "Source" / "ToSailTheStarrySky"
PLAYER = (SRC / "Private" / "TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
GROUND = (SRC / "Public" / "TSTSSReviewGrounding.h").read_text(encoding="utf-8")
OPENING = (SRC / "Private" / "TSTSSOpeningReviewWidget.cpp").read_text(encoding="utf-8")
NATIVE_TEST = (SRC / "Private" / "Tests" / "TSTSSReviewDockReturnTests.cpp").read_text(encoding="utf-8")
START_MAP = "/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2"


class OpeningDockSourceContract(unittest.TestCase):
    def test_new_game_opens_existing_playable_map(self):
        self.assertTrue((UNREAL / "Content" / (START_MAP.removeprefix("/Game/") + ".umap")).is_file())
        fn = OPENING.split("void UTSTSSOpeningReviewWidget::BeginJourney()", 1)[1]
        self.assertIn("FPackageName::DoesPackageExist(PreludeMap)", fn)
        self.assertIn("UGameplayStatics::OpenLevel(Controller, FName(*PreludeMap))", fn)
        self.assertIn(START_MAP, fn)
        self.assertNotIn("RemoveFromParent()", fn)

    def test_absent_map_does_not_fake_success(self):
        fn = OPENING.split("void UTSTSSOpeningReviewWidget::BeginJourney()", 1)[1]
        guard = fn.split("if (!FPackageName::DoesPackageExist(PreludeMap))", 1)[1]
        self.assertLess(guard.index("return;"), guard.index("UGameplayStatics::OpenLevel"))

    def test_recovery_is_review_only(self):
        for name in ("FirstWake_PreludeInteraction_V2", "VS01_DenithHarbor",
                     "VS06_SplashdownShore", "L_VS06_ShoreMagicEnemyGear_Review"):
            self.assertIn(name, GROUND)
        self.assertNotIn("VS04_SplashdownSea", GROUND)
        self.assertNotIn("VS03_FirstWakeSky", GROUND)
        self.assertIn("World->WorldType != EWorldType::PIE", PLAYER)
        self.assertIn("World->WorldType != EWorldType::Game", PLAYER)
        self.assertIn('StartsWith(TEXT("/Game/TSTSS/Review/"))', PLAYER)
        self.assertIn('bReviewNamespace, Scene, bHasSupportedReviewLocation', PLAYER)
        self.assertIn("#if !UE_BUILD_SHIPPING", PLAYER)

    def test_anchor_requires_walkable_support(self):
        self.assertIn("IsMovingOnGround()", PLAYER)
        self.assertIn("HasSupportedReviewFooting(World, Current)", PLAYER)
        self.assertIn("Hit.ImpactNormal.Z < 0.7f", PLAYER)
        self.assertIn("const FVector Offsets[]", PLAYER)
        self.assertIn("ECC_WorldStatic", PLAYER)

    def test_fall_uses_existing_anchor_without_story_mutation(self):
        self.assertIn("Current.Z < Anchor.Z - RecoveryDropCm", GROUND)
        self.assertIn("World->FindTeleportSpot", PLAYER)
        self.assertIn("TeleportTo(Candidate", PLAYER)
        tick = PLAYER.split("void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)", 1)[1].split(
            "void ATSTSSExplorerCharacter::SetupPlayerInputComponent", 1)[0]
        self.assertNotIn("FirstWakeState->AdvanceTo(", tick)
        self.assertNotIn("SaveProgress(", tick)
        self.assertNotIn("OpenLevel(", tick)

    def test_native_negative_controls_registered(self):
        for label in ("A sea fall is not auto-corrected", "No ground anchor cannot teleport",
                      "Grounded player cannot teleport", "Threshold equality does not rescue",
                      "NaN coordinates rejected"):
            self.assertIn(label, NATIVE_TEST)


if __name__ == "__main__":
    unittest.main()
