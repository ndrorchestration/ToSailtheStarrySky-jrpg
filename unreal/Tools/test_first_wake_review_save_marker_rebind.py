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

    def test_native_review_negative_and_positive_cases_added(self):
        self.assertIn("Quickload reactivates not-yet-launched visibility",NATIVE)
        self.assertIn("Saved-complete flyer remains transparent",NATIVE)
        self.assertIn("Uninspected lift remains interactable",NATIVE)
        self.assertIn("Already inspected Lift stops blocking",NATIVE)
        self.assertIn("Production-like actor keeps visibility blocking",NATIVE)

if __name__=="__main__":
    unittest.main()
