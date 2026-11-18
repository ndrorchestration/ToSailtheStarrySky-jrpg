"""Engine-free cross-file guard for the V5 docked ship's non-authorizing sea pose.

Source checks do not prove Unreal render, build, player view or gameplay.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky"
ACTOR = (ROOT / "Private/AureateWakePreviewActor.cpp").read_text(encoding="utf8")
PAWN = (ROOT / "Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HEADER = (ROOT / "Public/TSTSSFirstWakeState.h").read_text(encoding="utf8")

def method_body(source: str, name: str, following: str) -> str:
    first = source.index(name)
    last = source.index(following, first)
    return source[first:last]

class DockedSeabourneSource(unittest.TestCase):
    def test_docked_pose_restricted_to_unstarted_runtime_v5_proxy(self):
        body = method_body(ACTOR,
            "bool AAureateWakePreviewActor::StageDockedSeabourneReviewPose()",
            "void AAureateWakePreviewActor::BeginPlay()")
        for token in (
            "#if WITH_EDITOR", "EWorldType::PIE", "EWorldType::Game",
            "NM_Standalone", 'StartsWith(TEXT("/Game/TSTSS/Review/"))',
            'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
            'TEXT("TSTSS_DOCKED_WAKE_REVIEW_SHIP_PROXY")',
            "IsValid(BoundReviewStory.Get())", "bTransitioning",
            "SnapToForm(EAureateWakeForm::Seaborne)",
            "mode_authority=0", "saved_map_unchanged=1",
        ):
            self.assertIn(token, body)
        self.assertNotIn("RequestForm(", body)
        self.assertNotIn("AdvanceTo(", body)
        self.assertIn("#else\n    return false;", body)

    def test_harbor_spawns_noncanonical_sea_form_before_quest(self):
        body = method_body(PAWN, "void StageDockedWakeReview(UWorld* World)",
                           "void StageEarnedEngineRoomReview(")
        self.assertEqual(body.count("StageDockedSeabourneReviewPose()"), 1)
        self.assertLess(body.index('SetActorLabel(TEXT("TSTSS_DOCKED_WAKE_REVIEW_SHIP_PROXY"))'),
                        body.index("StageDockedSeabourneReviewPose()"))
        self.assertLess(body.index("StageDockedSeabourneReviewPose()"),
                        body.index('Captain->Tags.AddUnique(TEXT("TSTSS_DOCKED_WAKE_STAGED"))'))
        self.assertIn('TEXT("TSTSS_DOCKED_WAKE_REVIEW_HOLD ship_seabourne_pose")', body)

    def test_unstarted_story_never_acquires_ship_mode_authority(self):
        body = method_body(HEADER, "FName GetReviewShipMode() const",
                           "bool IsReviewShipModeAuthorized(")
        self.assertIn("if (!bStarted) return NAME_None;", body)
        self.assertIn('FName(TEXT("Seabourne"))', body)
        self.assertIn('FName(TEXT("Skybourne"))', body)
        self.assertIn("IsSeabourneRecoveryLocked()", body)

    def test_unstarted_story_reset_retracts_unauthorized_flight_geometry(self):
        # A reset can arrive both during ascent and after ascent completes.
        # This source guard is not a substitute for the existing Unreal test.
        tick = ACTOR.split(
            "void AAureateWakePreviewActor::Tick(float DeltaSeconds)", 1)[1]
        gate = tick.split("    if (!bTransitioning)", 1)[0]
        self.assertIn("if (Authorized == NAME_None)", gate)
        self.assertIn(
            "if (bTransitioning || CurrentForm != EAureateWakeForm::Seaborne)",
            gate)
        self.assertIn("SnapToForm(EAureateWakeForm::Seaborne);", gate)
        self.assertNotIn("SnapToForm(EAureateWakeForm::Skyborne);", gate)

if __name__ == "__main__":
    unittest.main()
