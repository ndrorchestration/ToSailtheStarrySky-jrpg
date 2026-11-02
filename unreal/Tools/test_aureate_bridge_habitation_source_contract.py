#!/usr/bin/env python3
"""Engine-free fail-closed source contract for the opt-in bridge/habitation review.

Does not replace UE 5.8 native build/automation or swept collision.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "Source/ToSailTheStarrySky/Public/AureateWakePreviewActor.h"
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"


def check_contract(header: str, source: str):
    h = (
        "bool bPreviewCentralBridgeHabitation = false;",
        "TObjectPtr<USceneComponent> BridgeHabitationPivot;",
        "TObjectPtr<UStaticMeshComponent> LivingQuartersEnvelope;",
        "FRotator SkyborneHabitationReviewRotation = FRotator::ZeroRotator;",
        "FRotator SeaborneHabitationReviewRotation = FRotator::ZeroRotator;",
        "FRotator SubmersibleHabitationReviewRotation = FRotator::ZeroRotator;",
        "bool RefreshCentralBridgeHabitationReview();",
        "bool bHabitationReviewLatchedForTransition = false;",
        "bool HasFiniteHabitationReviewRotation(EAureateWakeForm Form) const;",
    )
    c = (
        'BridgeHabitationPivot = CreateDefaultSubobject<USceneComponent>(TEXT("BridgeHabitationPivot"));',
        "BridgeHabitationPivot->SetupAttachment(VesselRoot);",
        "ForwardBridge->SetupAttachment(BridgeHabitationPivot);",
        'LivingQuartersEnvelope = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("LivingQuartersEnvelope"));',
        "LivingQuartersEnvelope->SetupAttachment(BridgeHabitationPivot);",
        "LivingQuartersEnvelope->SetVisibility(false); // No added default art or habitation geometry.",
        "BridgeHabitationPivot->SetRelativeLocation(FVector(0, 0, 50));",
        "ForwardBridge->SetRelativeLocation(FVector(0, 0, 80));",
        "ForwardBridge->SetRelativeLocation(FVector(240, 0, 95));",
        "LivingQuartersEnvelope->SetVisibility(true);",
        "BridgeHabitationPivot->SetRelativeRotation(FQuat::Slerp(",
        "StartHabitationReviewRotation, TargetHabitationReviewRotation, Smooth).GetNormalized());",
        "StartHabitationReviewRotation = BridgeHabitationPivot",
        "TargetHabitationReviewRotation = bHabitationReviewLatchedForTransition",
        "bHabitationReviewLatchedForTransition = bPreviewCentralBridgeHabitation;",
        "if (bHabitationReviewLatchedForTransition && BridgeHabitationPivot)",
        "bHabitationReviewLatchedForTransition = false;",
        "if (!RefreshCentralBridgeHabitationReview()) return false;",
        "bool AAureateWakePreviewActor::HasFiniteHabitationReviewRotation(EAureateWakeForm Form) const",
        "return !SkyborneHabitationReviewRotation.ContainsNaN();",
        "return !SeaborneHabitationReviewRotation.ContainsNaN();",
        "return !SubmersibleHabitationReviewRotation.ContainsNaN();",
        "if (bPreviewCentralBridgeHabitation &&\n        !HasFiniteHabitationReviewRotation(CurrentForm))",
        "!HasFiniteHabitationReviewRotation(RequestedForm)",
        "(bPreviewCentralBridgeHabitation &&",
        "CurrentForm == EAureateWakeForm::Orbiter",
        "RequestedForm == EAureateWakeForm::Orbiter && !bAllowOrbiterPreview",
    )
    for token in h:
        if header.count(token) != 1:
            raise ValueError("Header review-pivot contract changed: " + token)
    for token in c:
        if token not in source:
            raise ValueError("C++ review-pivot contract changed: " + token)
    # Preserve default hazard-free review-only art and split form authority.
    if source.count("SetupPreviewMesh(LivingQuartersEnvelope, Shape);") != 1:
        raise ValueError("Quarters must use noncolliding review mesh setup")
    if "bAllowOrbiterPreview = true;" in header or "bAllowOrbiterPreview = true;" in source:
        raise ValueError("Starbourne preview authorization changed")
    return True


class BridgeHabitationSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.header = HEADER.read_text(encoding="utf-8")
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_current_source_contract(self):
        self.assertTrue(check_contract(self.header, self.source))

    def test_mutant_removing_invalid_target_guard_is_rejected(self):
        changed = self.source.replace(
            "!HasFiniteHabitationReviewRotation(RequestedForm)",
            "false /* invalid requested angle guard removed */")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_removing_active_refresh_guard_is_rejected(self):
        changed = self.source.replace(
            "if (bPreviewCentralBridgeHabitation &&\n        !HasFiniteHabitationReviewRotation(CurrentForm))",
            "if (false /* active-angle gate removed */)")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_skipping_finite_seaborne_check_is_rejected(self):
        changed = self.source.replace(
            "return !SeaborneHabitationReviewRotation.ContainsNaN();",
            "return true;")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_nonfinite_native_regressions_registered(self):
        native = (ROOT / "Source/ToSailTheStarrySky/Private/Tests/AureateBridgeHabitationReviewTests.cpp").read_text(encoding="utf-8")
        self.assertIn("NaN destination angle rejects a form request atomically", native)
        self.assertIn("Infinity in active review angle blocks movement", native)
        self.assertIn("Opt out recovers even with an invalid stored editor angle", native)
        self.assertIn("std::numeric_limits<float>::quiet_NaN()", native)
        self.assertIn("std::numeric_limits<float>::infinity()", native)

    def test_mutant_enabling_review_by_default_rejected(self):
        changed = self.header.replace(
            "bool bPreviewCentralBridgeHabitation = false;",
            "bool bPreviewCentralBridgeHabitation = true;")
        with self.assertRaisesRegex(ValueError, "Header"):
            check_contract(changed, self.source)

    def test_mutant_uncoupling_quarters_rejected(self):
        changed = self.source.replace(
            "LivingQuartersEnvelope->SetupAttachment(BridgeHabitationPivot);",
            "LivingQuartersEnvelope->SetupAttachment(VesselRoot);")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_uncoupling_dome_rejected(self):
        changed = self.source.replace(
            "ForwardBridge->SetupAttachment(BridgeHabitationPivot);",
            "ForwardBridge->SetupAttachment(VesselRoot);")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_exposing_quarters_by_default_rejected(self):
        changed = self.source.replace(
            "LivingQuartersEnvelope->SetVisibility(false); // No added default art or habitation geometry.",
            "LivingQuartersEnvelope->SetVisibility(true); // No added default art or habitation geometry.")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_dropping_midflight_latch_rejected(self):
        changed = self.source.replace(
            "bHabitationReviewLatchedForTransition = bPreviewCentralBridgeHabitation;",
            "bHabitationReviewLatchedForTransition = true;")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_removing_central_orbiter_rejection_rejected(self):
        changed = self.source.replace(
            "(bPreviewCentralBridgeHabitation &&",
            "(false /* REVIEW GATE REMOVED */ &&")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)

    def test_mutant_removing_pivot_motion_rejected(self):
        changed = self.source.replace(
            "BridgeHabitationPivot->SetRelativeRotation(FQuat::Slerp(",
            "BridgeHabitationPivot->SetRelativeRotation(FQuat::Identity /*")
        with self.assertRaisesRegex(ValueError, r"C\+\+"):
            check_contract(self.header, changed)


if __name__ == "__main__":
    unittest.main()
