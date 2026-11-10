"""P0-4 engine-free contracts for explicit two-press Continue.

These assertions do not claim real Unreal F7 input, disk restart, or ship-state
restoration; separate native and actual D3D11 PIE receipts are required.
"""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
private=ROOT/"Source/ToSailTheStarrySky/Private"
public=ROOT/"Source/ToSailTheStarrySky/Public"
actor=(private/"TSTSSExplorerCharacter.cpp").read_text()
manifest=(private/"TSTSSReviewContinueManifest.cpp").read_text()
header=(public/"TSTSSReviewContinueManifest.h").read_text()
input_config=(ROOT/"Config/DefaultInput.ini").read_text()
hud=(private/"TSTSSFirstWakeReviewHUD.cpp").read_text()
native=(private/"Tests/TSTSSFirstWakeInteractionIntegrationTests.cpp").read_text()

class ExplicitContinueContract(unittest.TestCase):
    def test_separate_visible_f7_action_and_two_step_preview(self):
        self.assertIn('+ActionMappings=(ActionName="ReviewContinue",Key=F7)',input_config)
        self.assertIn('BindAction(TEXT("ReviewContinue")',actor)
        self.assertIn("F7: Continue preview/confirm",hud)
        self.assertIn("TSTSS_PIE_REVIEW_CONTINUE_PREVIEW",actor)
        self.assertIn("TSTSS_PIE_REVIEW_CONTINUE_ACCEPT",actor)
        self.assertIn("World->GetTimeSeconds() + 30.f",actor)
        self.assertIn("PendingReviewContinueDigest == Digest",actor)
        self.assertLess(actor.index("if (!bConfirm)"),actor.index("if (!LoadFirstWake(ReviewPrimarySlot))"))

    def test_f9_stays_session_scoped_and_no_automatic_begin_play_resume(self):
        self.assertIn("if (bPIE && !bPIEReviewQuickSlotOwned)",actor)
        self.assertIn("bPIEReviewQuickSlotOwned = false;",actor)
        begin=actor.split("void ATSTSSExplorerCharacter::BeginPlay()",1)[1].split(
            "void ATSTSSExplorerCharacter::SetupPlayerInputComponent",1)[0]
        self.assertNotIn("LoadFirstWake(",begin)
        self.assertNotIn("ReviewContinue(",begin)

    def test_both_primary_and_manifest_preexisting_block_unauthorized_pie_f6(self):
        body=actor.split("void ATSTSSExplorerCharacter::QuickSave()",1)[1].split(
            "void ATSTSSExplorerCharacter::QuickLoad()",1)[0]
        self.assertIn("DoesSaveGameExist(Slot, 0)",body)
        self.assertIn('TEXT("tstss_prelude_pie_manifest_v1")',body)
        self.assertIn("if (bPIE && bSavedStory)",body)
        self.assertIn("SaveReviewContinueBinding(Slot)",body)
        self.assertIn("bPIEReviewQuickSlotOwned = true",body)

    def test_review_only_and_actual_save_file_integrity_binding(self):
        self.assertIn("World->WorldType != EWorldType::PIE",actor)
        self.assertIn("LexToString(FIoHash::HashBuffer(Bytes.GetData()",actor)
        self.assertIn("Bytes.Num() > 262144",actor)
        self.assertIn('TEXT("SaveGames")',actor)
        self.assertIn('Slot + TEXT(".sav")',actor)
        self.assertIn("PrimaryBlake3_160.Len() != 40",manifest)
        self.assertIn("ReviewMapPackage != ExpectedMapPackage",manifest)
        self.assertIn("ProjectRoot.Equals(ExpectedProjectRoot",manifest)
        self.assertIn("PrimarySlot != ExpectedSlot",manifest)
        self.assertIn("SavedBeat != Primary->FirstWakeBeat",manifest)

    def test_flight_rejected_until_ship_state_and_roster_are_supported(self):
        self.assertIn("Primary->PartyRoster.Num() != 0",manifest)
        self.assertIn("ETSTSSFirstWakeBeat::Launched",manifest)
        self.assertIn("return false;",manifest)
        self.assertIn("PrimarySchemaVersion != UTSTSSSaveGame::CurrentVersion",manifest)
        self.assertIn("ReviewVersion != CurrentReviewVersion",manifest)
        self.assertIn("TSTSS_FIRST_WAKE_PIE_CONTINUE_V1",header)
        self.assertIn("Uncaptured ship flight cannot be restored",native)

    def test_position_bound_finite_and_preflighted_before_restore(self):
        self.assertIn("IsFiniteLocation(SavedPawnLocation)",manifest)
        self.assertIn("IsFiniteRotation(SavedPawnRotation)",manifest)
        self.assertIn("World->FindTeleportSpot(this, TargetLocation, TargetRotation)",actor)
        self.assertIn("FVector::Dist(TargetLocation, Manifest->SavedPawnLocation) > 50.f",actor)
        self.assertLess(actor.index("World->FindTeleportSpot(this, TargetLocation, TargetRotation)"),
                        actor.index("if (!LoadFirstWake(ReviewPrimarySlot))"))
        self.assertIn("SetActorLocationAndRotation(OriginalLocation, OriginalRotation",actor)

    def test_foreign_and_corrupt_reviews_refused_without_story_mutation(self):
        begin=actor.split("void ATSTSSExplorerCharacter::ReviewContinue()",1)[1]
        self.assertLess(begin.index("LoadBoundReviewContinueCandidate("),
                        begin.index("Trial->Restore("))
        self.assertLess(begin.index("Trial->Restore("),
                        begin.index("if (!LoadFirstWake(ReviewPrimarySlot))"))
        for token in ("missing_corrupt_foreign_or_flight_save",
                      "invalid_story_state","unsafe_saved_player_location",
                      "story_restore_failed","TSTSS_PIE_REVIEW_CONTINUE_REJECT"):
            self.assertIn(token,begin)
        for token in ("Foreign source project cannot Continue",
                      "Mutated primary bytes cannot Continue",
                      "Unknown future sidecar rejected",
                      "Out-of-bounds pawn location rejected"):
            self.assertIn(token,native)

if __name__=="__main__":
    unittest.main()
