"""Source gates for the non-shipping V5 interaction/readability and material pass.

No gameplay acceptance is inferred until Win64 native build, tests and a
directly captured UE runtime review have passed at the same exact source HEAD.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
S = ROOT / "Source/ToSailTheStarrySky"
ACTOR = (S / "Private/TSTSSMilestoneActor.cpp").read_text(encoding="utf-8")
ACTOR_H = (S / "Public/TSTSSMilestoneActor.h").read_text(encoding="utf-8")
PAWN = (S / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
PAWN_H = (S / "Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")
HUD = (S / "Private/TSTSSFirstWakeReviewHUD.cpp").read_text(encoding="utf-8")
REACH = (S / "Public/TSTSSInteractionReach.h").read_text(encoding="utf-8")


class ReadableInteractionContract(unittest.TestCase):
    def test_world_beacon_is_cosmetic_and_scoped(self):
        self.assertIn("ReviewBeacon = CreateDefaultSubobject<UTextRenderComponent>", ACTOR)
        self.assertIn("ReviewBeacon->SetCollisionEnabled(ECollisionEnabled::NoCollision)", ACTOR)
        self.assertIn("IsAuthorizedReviewMilestoneWorld(GetWorld(), GetActorLabel())", ACTOR)
        self.assertIn("ReviewBeacon->SetVisibility(bAvailable)", ACTOR)
        self.assertIn("bReviewBeaconAvailable == bAvailable", ACTOR)
        self.assertIn("void UpdateReviewBeacon(const UTSTSSFirstWakeState* State)", ACTOR_H)
        self.assertIn("ReviewBeacon->SetTextRenderColor(FColor(255, 205, 96))", ACTOR)

    def test_beacon_availability_follows_story_not_a_shortcut(self):
        helper = ACTOR.split(
            "bool ATSTSSMilestoneActor::IsReviewActionable(", 1
        )[1].split("void ATSTSSMilestoneActor::UpdateReviewBeacon(", 1)[0]
        self.assertIn("IsAuthorizedReviewMilestoneWorld(", helper)
        self.assertIn("State->GetInspectionMask()", helper)
        self.assertIn("State->AreInspectionsComplete()", helper)
        self.assertIn("State->HasStarted()", helper)
        self.assertIn("ETSTSSFirstWakeBeat::SeaContact", helper)
        self.assertIn("ETSTSSFirstWakeBeat::FlotationConfirmed", helper)
        for forbidden in ("AdvanceTo(", "InspectStation(", "Restore(", "SaveGameToSlot(",
                          "AdvanceWaterBeat(", "OpenLevel("):
            self.assertNotIn(forbidden, helper)

    def test_prompt_uses_real_e_trace_and_pawn_reach(self):
        self.assertIn("FString GetReviewAimStatus() const;", PAWN_H)
        e = PAWN.split("void ATSTSSExplorerCharacter::Interact()", 1)[1].split(
            "void ATSTSSExplorerCharacter::ShowObjectiveReview()", 1
        )[0]
        read_only = PAWN.split(
            "FString ATSTSSExplorerCharacter::GetReviewAimStatus() const", 1
        )[1].split("void ATSTSSExplorerCharacter::Interact()", 1)[0]
        for fragment in (
            "TSTSSInteractionReach::GetCameraTraceLength(",
            "LineTraceSingleByChannel(",
            "FollowCamera->GetForwardVector()",
            "ECC_Visibility",
            "TSTSSInteractionReach::IsInsidePlayerReach(",
            "Hit.ImpactPoint, InteractionDistance",
        ):
            self.assertIn(fragment, e)
            self.assertIn(fragment, read_only)
        self.assertIn("Marker->IsReviewActionable(FirstWakeState)", read_only)
        self.assertIn("World->GetNetMode() != NM_Standalone", read_only)
        self.assertIn("MOVE CLOSER", read_only)
        self.assertIn("LOCKED", read_only)
        for forbidden in ("TryActivate(", "AdvanceTo(", "QueueShore(", "OpenLevel(",
                          "SaveGameToSlot(", "SetActorLocation("):
            self.assertNotIn(forbidden, read_only)

    def test_hud_has_high_contrast_and_follows_true_aim(self):
        self.assertIn("Explorer->GetReviewAimStatus()", HUD)
        self.assertIn("FOLLOW THE GOLD MARKER", HUD)
        self.assertIn("Width = FMath::Min(690.f, Canvas->ClipX - 48.f)", HUD)
        self.assertIn("GEngine->GetMediumFont()", HUD)
        self.assertIn("Canvas->ClipY - 88.f", HUD)
        self.assertIn("DrawRect(Accent, Canvas->ClipX * .5f - 3.f", HUD)
        self.assertIn("#if !UE_BUILD_SHIPPING", HUD)
        self.assertNotIn("AdvanceTo(", HUD)

    def test_native_material_pass_is_one_review_world_only(self):
        src = PAWN.split("void ApplyV5HarborReviewLookdev(", 1)[1].split(
            "#endif", 1
        )[0]
        self.assertIn("NM_Standalone", src)
        self.assertIn('TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', src)
        self.assertIn("World->GetOutermost()->GetName().StartsWith", src)
        self.assertIn("GetStaticMeshComponent()->SetMaterial(0, Loaded[Index])", src)
        self.assertIn("bOverride_AutoExposureBias = true", src)
        self.assertIn("AutoExposureBias = -2.2f", src)
        for name in ("Harbor_TraversalFloor", "Ocean_VISUAL_ONLY_NO_BUOYANCY",
                     "QuaysideWall", "GangwayVisualMarker", "EngineBayVisualMarker",
                     "HarborStorehouseBlockout"):
            self.assertIn("TSTSS_PRELUDE_REVIEW_" + name, src)
        for name in ("TSTSS_wood", "TSTSS_teal_glass", "TSTSS_dark_iron",
                     "TSTSS_brass", "TSTSS_patina"):
            self.assertIn('TEXT("' + name + '")', src)
        self.assertIn("return; // Never partially re-skin", src)
        for forbidden in ("SaveCurrentLevel", "SaveMap(", "SaveGameToSlot(",
                          "SetCollisionEnabled(", "AdvanceWaterBeat(", "TeleportTo("):
            self.assertNotIn(forbidden, src)

    def test_legacy_signs_hidden_without_mutating_source_maps(self):
        section = PAWN.split("void ATSTSSExplorerCharacter::Tick(", 1)[1].split(
            "void ATSTSSExplorerCharacter::SetupPlayerInputComponent(", 1
        )[0]
        self.assertIn("UpdateReviewBeacon(FirstWakeState)", section)
        self.assertIn("TSTSS_PRELUDE_REVIEW_SIGN_", section)
        self.assertIn("It->SetActorHiddenInGame(true)", section)
        self.assertIn("Scene == TEXT(\"VS05_DenithFuelShanty\")", section)
        self.assertNotIn("EditorLoadingAndSavingUtils", section)


if __name__ == "__main__":
    unittest.main()
