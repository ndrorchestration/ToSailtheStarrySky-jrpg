"""Source contract for in-PIE marker rebind after successful F9 story restore.

Native Unreal automated actors and actual F6/F9 replay are separate gates.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
HEADER=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSMilestoneActor.h").read_text()
MILESTONE=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSMilestoneActor.cpp").read_text()
CHARACTER=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text()
NATIVE=(ROOT/"Source/ToSailTheStarrySky/Private/Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp").read_text()

class FirstWakeReviewRestoreCollisionContract(unittest.TestCase):
    def test_rebind_method_has_editor_only_declaration_and_definition(self):
        self.assertIn("#if WITH_EDITOR\n    // Synchronize review-only marker rays", HEADER)
        self.assertIn("void ReconcileReviewCollisionAfterRestore(", HEADER)
        self.assertIn("#if WITH_EDITOR\nvoid ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(", MILESTONE)

    def test_rebind_is_pie_and_review_namespaces_only(self):
        self.assertIn("World->WorldType != EWorldType::PIE", MILESTONE)
        self.assertIn("TSTSS_PRELUDE_REVIEW_", MILESTONE)
        self.assertIn("TSTSS_SPLASHDOWN_GREYBOX_", MILESTONE)
        self.assertIn("!IsValid(InteractionMesh)", MILESTONE)

    def test_rebind_respects_inspection_mask_and_ordered_story_beats(self):
        self.assertIn("State->GetInspectionMask() & StationBit", MILESTONE)
        self.assertIn("static_cast<uint8>(State->GetCurrentBeat())", MILESTONE)
        self.assertIn("const ECollisionResponse ReviewResponse =", MILESTONE)
        self.assertIn("bAlreadyConsumed ? ECR_Ignore : ECR_Block;", MILESTONE)

    def test_restore_preserves_pass_through_and_editor_save_key(self):
        rebind=MILESTONE.split("void ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(",1)[1]
        self.assertIn("SetCollisionResponseToChannel(ECC_Pawn, ECR_Ignore)",rebind)
        self.assertNotIn("SetCollisionResponseToChannel(ECC_Pawn, ReviewResponse)",rebind)
        self.assertIn('BindAction(TEXT("PIEReviewQuickSave")',CHARACTER)
        self.assertIn("Quickload preserves pass-through pawn movement",NATIVE)

    def test_rebind_does_not_allow_physics_milestones(self):
        rebind=MILESTONE.split("void ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore(",1)[1]
        self.assertIn("Milestone == ETSTSSFirstWakeBeat::SeaContact",rebind)
        self.assertIn("Milestone == ETSTSSFirstWakeBeat::FlotationConfirmed",rebind)
        for forbidden in ("AdvanceWaterBeat(", "SaveGameToSlot(", "SetSimulatePhysics("):
            self.assertNotIn(forbidden,rebind)

    def test_load_reconciles_only_after_a_successful_restore(self):
        load=CHARACTER.split("bool ATSTSSExplorerCharacter::LoadFirstWake(",1)[1]
        self.assertIn("const bool bRestored = FirstWakeState->Restore(",load)
        self.assertIn("if (bRestored && World && World->WorldType == EWorldType::PIE)",load)
        self.assertIn("TActorIterator<ATSTSSMilestoneActor>",load)
        self.assertIn("It->ReconcileReviewCollisionAfterRestore(FirstWakeState);",load)
        self.assertIn("TSTSS_PIE_REVIEW_LOAD_REBOUND",load)
        self.assertLess(load.index("const bool bRestored"),load.index("for (TActorIterator"))

    def test_stale_pie_slot_guard_remains_unchanged(self):
        self.assertIn("if (bPIE && !bPIEReviewQuickSlotOwned)",CHARACTER)
        self.assertIn("existing PIE quicksave protected; refusing overwrite",CHARACTER)

    def test_native_transient_pie_world_stays_fail_closed(self):
        # The native integration fixture creates a named transient PIE world,
        # not the actual /Game/TSTSS/Review/... package. Positive ray release
        # authority belongs only to the scoped real-review-world helper.
        self.assertIn("TSTSSConsumedSplashdownReviewTest", NATIVE)
        self.assertIn("Quickload reactivates not-yet-launched visibility", NATIVE)
        self.assertIn("Accepted launch in unrelated transient PIE keeps visibility blocking", NATIVE)
        self.assertIn("Saved-complete flyer stays blocked outside package-scoped review maps", NATIVE)
        self.assertIn("Uninspected lift remains interactable", NATIVE)
        self.assertIn("Already inspected Lift cannot alter marker ray outside review map", NATIVE)
        self.assertIn("Production-like actor keeps visibility blocking", NATIVE)
        self.assertIn("IsAuthorizedReviewMilestoneWorld(World, GetActorLabel())", MILESTONE)
        self.assertIn("World->GetOutermost()->GetName().StartsWith", MILESTONE)
        self.assertIn("VS05_DenithFuelShanty", MILESTONE)


    def test_native_positive_review_world_fixture_is_exact_scoped(self):
        # A denied transient world is necessary but cannot prove that
        # actual allowlisted review maps release accepted or restored rays.
        self.assertIn('#include "UObject/Package.h"', NATIVE)
        self.assertIn('TEXT("/Game/TSTSS/Review/VS05_DenithFuelShanty")', NATIVE)
        self.assertIn('TEXT("/Game/TSTSS/Review/FirstWake_PreludeInteraction_V2")', NATIVE)
        self.assertIn('FName(TEXT("VS05_DenithFuelShanty"))', NATIVE)
        self.assertIn('FName(TEXT("FirstWake_PreludeInteraction_V2"))', NATIVE)
        self.assertIn("AllowedShantyWorld->SpawnActor<ATSTSSMilestoneActor>()", NATIVE)
        self.assertIn("AllowedPreludeWorld->SpawnActor<ATSTSSMilestoneActor>()", NATIVE)
        self.assertIn("Authorized VS05 accepted launch releases E ray", NATIVE)
        self.assertIn("Authorized VS05 restored launch blocks E ray again", NATIVE)
        self.assertIn("Authorized Prelude completed flyer releases E ray", NATIVE)
        self.assertIn("Uninspected authorized Lift blocks E ray", NATIVE)
        self.assertIn("Inspected authorized Lift releases E ray", NATIVE)
        self.assertIn("Unrelated label in review map stays ray blocking", NATIVE)
        self.assertIn("Accepted launch in unrelated transient PIE keeps visibility blocking", NATIVE)
        self.assertIn("AllowedPreludeWorld->DestroyWorld(false)", NATIVE)
        self.assertIn("AllowedShantyWorld->DestroyWorld(false)", NATIVE)

if __name__=="__main__":
    unittest.main()
