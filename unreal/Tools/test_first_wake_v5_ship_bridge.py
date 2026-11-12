"""Source-only, negative-control acceptance for a review ship-interior bridge.

No Unreal build, packaged game, native PIE or visual approval is claimed.
"""
from pathlib import Path
import hashlib
import unittest

UNREAL = Path(__file__).resolve().parents[1]
SOURCE = UNREAL / "Source/ToSailTheStarrySky"
TRAVEL = (SOURCE / "Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf-8")
MILESTONE = (SOURCE / "Private/TSTSSMilestoneActor.cpp").read_text(encoding="utf-8")
PAWN = (SOURCE / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
NATIVE = (SOURCE / "Private/Tests/TSTSSFirstWakeReviewObjectiveTests.cpp").read_text(encoding="utf-8")


class FirstWakeV5ShipBridgeSource(unittest.TestCase):
    def test_original_maps_and_verified_v5_are_byte_identical(self):
        expected = {
            "FirstWake_PreludeInteraction_V2":
                "4c96f1fb28fe4af91b879977e473c20de32bd933f741a5384bb8403a00254b80",
            "FirstWake_PreludeInteraction_V5_VisualReview":
                "ff2b5c1423a370c4ac318b9b241088d8f20fec5eee993c998c2a5ed335cbb299",
        }
        for name, sha in expected.items():
            p = UNREAL / "Content/TSTSS/Review" / (name + ".umap")
            self.assertEqual(hashlib.sha256(p.read_bytes()).hexdigest(), sha)
        for name in ("VS02_AureateInteriors", "VS03_FirstWakeSky"):
            self.assertTrue((UNREAL / "Content/TSTSS/Review/VerticalSlice" / (name + ".umap")).is_file())

    def test_v5_routes_through_ship_without_early_launch(self):
        self.assertIn('constexpr const TCHAR* ShipName = TEXT("VS02_AureateInteriors");', TRAVEL)
        self.assertIn('SourceMap == VisualReviewPreludeName', TRAVEL)
        self.assertIn('"/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors"', TRAVEL.replace("TEXT(", "").replace(")", ""))
        self.assertIn('SourceMap == ShipName && Beat == ETSTSSFirstWakeBeat::EngineeringChecked', TRAVEL)
        self.assertIn('"/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky"', TRAVEL.replace("TEXT(", "").replace(")", ""))
        self.assertIn('(IsPreludeScene(SourceMap) && SourceMap != VisualReviewPreludeName)', TRAVEL)
        self.assertIn('SourceMap == ShipName) &&', TRAVEL)
        self.assertIn('SourceMap != VisualReviewPreludeName', TRAVEL)
        self.assertIn('bPending = true;', TRAVEL)
        self.assertIn('FPackageName::DoesPackageExist(*Destination)', TRAVEL)
        self.assertIn('World->GetNetMode() != NM_Standalone', TRAVEL)
        self.assertIn('World->GetNetMode() == NM_Standalone', TRAVEL)
        self.assertEqual(TRAVEL.count('StartsWith(TEXT("/Game/TSTSS/Review/"))'), 3)
        self.assertIn('Target.StartsWith(TEXT("/Game/TSTSS/Review/"))', TRAVEL)
        self.assertIn('UGameplayStatics::GetCurrentLevelName(World, true) == FPackageName::GetShortName(Target)', TRAVEL)
        # Original V2 diagnostic and V5 game path remain separate authorities.
        self.assertIn('const FString VisualPrelude(', NATIVE)
        self.assertIn('V5 opens ship before a launch event', NATIVE)
        self.assertIn('Ship departure requires inspections and opens only the sky review', NATIVE)
        self.assertIn('Boarded alone cannot leave ship', NATIVE)

    def test_keep_physical_water_and_post_splashdown_gates(self):
        section = TRAVEL.split("FString UTSTSSReviewShoreTravelSubsystem::NextReviewMap(", 1)[1].split(
            "bool UTSTSSReviewShoreTravelSubsystem::IsEligible(", 1)[0]
        self.assertIn('Beat == ETSTSSFirstWakeBeat::Launched', section)
        self.assertIn('Beat == ETSTSSFirstWakeBeat::FlotationConfirmed', section)
        self.assertIn('Beat == ETSTSSFirstWakeBeat::EmptyReserveInspected', section)
        for forbidden in ('AdvanceWaterBeat(', 'GrantPartyMember(', 'Starbourne', 'Lyra'):
            self.assertNotIn(forbidden, TRAVEL)
        self.assertNotIn('VS04_SplashdownSea', TRAVEL.split('if (SourceMap == ShipName', 1)[1].split('if (SourceMap == SkyName', 1)[0])

    def test_milestone_collision_reconciled_only_in_review_game_or_pie(self):
        self.assertIn('World->WorldType != EWorldType::PIE &&', MILESTONE)
        self.assertIn('World->WorldType != EWorldType::Game', MILESTONE)
        self.assertIn('World->GetNetMode() != NM_Standalone', MILESTONE)
        self.assertIn('StartsWith(TEXT("/Game/TSTSS/Review/"))', MILESTONE)
        self.assertIn('FirstWake_PreludeInteraction_V5_VisualReview', MILESTONE)
        self.assertIn('FirstWake_PreludeInteraction_V2', MILESTONE)
        self.assertIn('VS05_DenithFuelShanty', MILESTONE)
        self.assertIn('IsAuthorizedReviewMilestoneWorld(', MILESTONE)
        self.assertIn('SetCollisionResponseToChannel(ECC_Visibility, ECR_Ignore)', MILESTONE)
        self.assertIn('SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore)', MILESTONE)
        self.assertNotIn('FirstWake_PreludeInteraction_V3_VisualReview', MILESTONE)
        self.assertNotIn('FirstWake_PreludeInteraction_V4_VisualReview', MILESTONE)

    def test_do_not_replace_verified_w_e_input_or_fall_recovery(self):
        self.assertIn('TSTSSInteractionReach::IsInsidePlayerReach(', PAWN)
        self.assertIn('Milestone->TryActivate(FirstWakeState)', PAWN)
        self.assertIn('Travel->ConsumeShoreArrival(World, FirstWakeState)', PAWN)
        self.assertIn('UTSTSSReviewShoreTravelSubsystem::IsEligible(', PAWN)
        self.assertIn('TSTSSReviewGrounding::IsWalkableReviewMap(Scene)', PAWN)


if __name__ == "__main__":
    unittest.main()
