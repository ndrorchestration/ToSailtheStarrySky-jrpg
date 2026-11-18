"""Engine-free regression guard for First Wake E-only shipboard feedback.

Source-contract checks do NOT prove Unreal ray hit, audio, voice, UI rendering,
collision, player accessibility, or native build/PIE acceptance.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source/ToSailTheStarrySky/Private"
PAWN = (ROOT / "TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
MARKER = (ROOT / "TSTSSMilestoneActor.cpp").read_text(encoding="utf8")

def span(source: str, start: str, end: str) -> str:
    at = source.index(start)
    stop = source.index(end, at + len(start))
    return source[at:stop]

def check_intercom_source(source: str) -> list[str]:
    errors = []
    intro = "void ShowEarnedFirstWakeEngineeringIntercom("
    start = source.find(intro)
    end = source.find("\n#endif", start) if start >= 0 else -1
    if start < 0 or end < 0:
        return ["missing engine-room intercom helper"]
    body = source[start:end]
    required = (
        "EWorldType::PIE", "EWorldType::Game", "NM_Standalone",
        'StartsWith(TEXT("/Game/TSTSS/Review/"))',
        'TEXT("VS02_AureateInteriors")',
        'StartsWith(TEXT("TSTSS_ENGINEROOM_REVIEW_"))',
        "State->GetCurrentBeat() == ETSTSSFirstWakeBeat::BoardedAureateWake",
        "State->GetCurrentBeat() == ETSTSSFirstWakeBeat::EngineeringChecked",
        "State->AreInspectionsComplete()",
        'Cue = TEXT("lift")', 'Cue = TEXT("pressure")',
        'Cue = TEXT("reserve")', 'Cue = TEXT("signoff")',
        "audio=NOT_VERIFIED launch=NOT_GRANTED",
        "if (!Cue || !Subtitle) return",
    )
    for token in required:
        if token not in body:
            errors.append("missing bounded intercom guard: " + token)
    # The call is within an accepted E branch, never upon a rejected ray,
    # pre-action inspection or camera-only scan.
    interaction = span(source, "void ATSTSSExplorerCharacter::Interact()",
                       "void ATSTSSExplorerCharacter::ShowObjectiveReview()")
    accepted = interaction.find("if (Milestone->TryActivate(FirstWakeState))")
    emitted = interaction.find("ShowEarnedFirstWakeEngineeringIntercom(")
    rejected = interaction.find("else\n                {\n                    // A valid, in-reach marker rejected")
    if not 0 <= accepted < emitted < rejected:
        errors.append("intercom not bound exclusively to successful E interaction")
    if interaction.count("ShowEarnedFirstWakeEngineeringIntercom(") != 1:
        errors.append("duplicate or absent intercom emission")
    for denied in ("AdvanceTo(", "InspectStation(", "SaveProgress(",
                   "QueueShore(", "RequestForm(", "LoadMap("):
        if denied in body:
            errors.append("intercom changed story/runtime via " + denied)
    return errors

def check_signoff_source(marker: str, pawn: str) -> list[str]:
    errors = []
    beacon = span(marker,
        "void ATSTSSMilestoneActor::UpdateReviewBeacon(",
        "bool ATSTSSMilestoneActor::TryActivate(")
    restored = marker[marker.index(
        "void ATSTSSMilestoneActor::ReconcileReviewCollisionAfterRestore("):]
    stage = span(pawn, "void StageEarnedEngineRoomReview(",
                 "void ShowEarnedFirstWakeEngineeringIntercom(")
    for label, body, required in (
        ("beacon", beacon,
         ('TEXT("TSTSS_ENGINEROOM_REVIEW_EngineeringApproval")',
          "bAvailable ? ECR_Block : ECR_Ignore",
          "bShipboardFinalSignoff && !bAvailable")),
        ("restore", restored,
         ('TEXT("TSTSS_ENGINEROOM_REVIEW_EngineeringApproval")',
          "!IsReviewActionable(State)", "bAlreadyConsumed = true")),
        ("stage", stage,
         ('if (!Item.bInspection)', "ECC_Visibility, ECR_Ignore",
          "Shape->SetVisibility(false, false)")),
    ):
        for token in required:
            if token not in body:
                errors.append(label + " missing signoff restraint: " + token)
    return errors

class EarnedEngineeringIntercomSource(unittest.TestCase):
    def test_intercom_only_after_real_accepted_e(self):
        self.assertEqual(check_intercom_source(PAWN), [])

    def test_signoff_not_targetable_until_all_inspections(self):
        self.assertEqual(check_signoff_source(MARKER, PAWN), [])

    def test_harbor_or_proxy_mutation_rejected(self):
        mutated = PAWN.replace('TEXT("VS02_AureateInteriors")',
            'TEXT("FirstWake_PreludeInteraction_V5_VisualReview")', 1)
        # Mutate inside the helper, not an unrelated earlier scene.
        start = mutated.index("void ShowEarnedFirstWakeEngineeringIntercom(")
        altered = mutated[:start] + mutated[start:].replace(
            'TEXT("VS02_AureateInteriors")', 'TEXT("VS03_FirstWakeSky")', 1)
        self.assertTrue(check_intercom_source(altered))

    def test_early_intercom_mutation_rejected(self):
        mutated = PAWN.replace(
            "if (Milestone->TryActivate(FirstWakeState))\n                {",
            "if (Milestone->TryActivate(FirstWakeState))\n                {\n"
            "                    ShowEarnedFirstWakeEngineeringIntercom(GetWorld(), Milestone, FirstWakeState);",
            1)
        self.assertTrue(check_intercom_source(mutated))

    def test_broken_signoff_beacon_mutation_rejected(self):
        mutated = MARKER.replace("bAvailable ? ECR_Block : ECR_Ignore",
                                 "ECR_Block", 1)
        self.assertTrue(check_signoff_source(mutated, PAWN))

    def test_broken_restore_signoff_mutation_rejected(self):
        mutated = MARKER.replace("!IsReviewActionable(State)",
                                 "IsReviewActionable(State)", 1)
        self.assertTrue(check_signoff_source(mutated, PAWN))

if __name__ == "__main__":
    unittest.main()
