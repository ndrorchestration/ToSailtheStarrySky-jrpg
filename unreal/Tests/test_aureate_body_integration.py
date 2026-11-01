"""Fail-closed source contracts for the Unreal 5.8 approved-reference body intake.

No Unreal native engine is available in this hosted Python job. These checks
are required but cannot certify actual UHT compilation, asset import or renders.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky"
HEADER = (ROOT / "Public" / "AureateWakePreviewActor.h").read_text(encoding="utf-8")
CPP = (ROOT / "Private" / "AureateWakePreviewActor.cpp").read_text(encoding="utf-8")
NATIVE = (ROOT / "Private" / "Tests" / "AureateWakePreviewNativeTests.cpp").read_text(encoding="utf-8")


def function_body(name, next_name):
    begin = CPP.index(f"{name}()")
    end = CPP.index(next_name, begin + len(name))
    return CPP[begin:end]


BODY = CPP[
    CPP.index("bool AAureateWakePreviewActor::RefreshBodyReviewMeshes()"):
    CPP.index("void AAureateWakePreviewActor::RefreshRootSupportReview()")
]
REQUEST = CPP[
    CPP.index("bool AAureateWakePreviewActor::RequestForm("):
    CPP.index("bool AAureateWakePreviewActor::FinishOrdinaryPreviewTransitionForReview()")
]


class ApprovedReferenceBodyReview(unittest.TestCase):
    def test_default_off_and_separate_apply_state(self):
        self.assertIn("bool bUseAuthoredBodyReview = false;", HEADER)
        self.assertIn("bool bBodyReviewApplied = false;", HEADER)
        self.assertIn("return bBodyReviewApplied;", HEADER)

    def test_review_must_have_both_meshes(self):
        self.assertIn("!NewHull || !NewBridge", BODY)
        self.assertLess(BODY.index("!NewHull || !NewBridge"), BODY.index("Hull->SetStaticMesh(NewHull);"))
        self.assertLess(BODY.index("!NewHull || !NewBridge"), BODY.index("ForwardBridge->SetStaticMesh(NewBridge);"))

    def test_strict_review_only_asset_paths(self):
        self.assertIn("/Game/TSTSS/Review/ShipArt/HullCandidateV1/", BODY)
        self.assertIn("/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1/", BODY)
        self.assertIn("GetPathName().StartsWith", BODY)

    def test_conflicting_visual_modes_rejected(self):
        self.assertIn("if (bUseHullSilhouetteReview) return false;", BODY)
        self.assertIn("bUseHullSilhouetteReview", HEADER)

    def test_safe_state_checks_before_modification(self):
        for token in (
            "bTransitioning", "CurrentForm == EAureateWakeForm::Orbiter",
            "Wings.Num() != 4", "Hydrofoils.Num() != 2",
            "WingRootMounts.Num() != 4", "HydrofoilStruts.Num() != 2",
        ):
            self.assertIn(token, BODY)
            self.assertLess(BODY.index(token), BODY.index("Hull->SetStaticMesh(NewHull);"))

    def test_clean_fallback_restore(self):
        self.assertIn("if (!bUseAuthoredBodyReview)", BODY)
        self.assertIn("Hull->SetStaticMesh(DefaultCube);", BODY)
        self.assertIn("ForwardBridge->SetStaticMesh(DefaultCube);", BODY)
        self.assertIn("FVector(8.f, 1.5f, .65f)", BODY)
        self.assertIn("FVector(240.f, 0.f, 95.f)", BODY)
        self.assertIn("FVector(2.1f, 1.1f, 1.1f)", BODY)
        self.assertIn("bBodyReviewApplied = false;", BODY)

    def test_atomic_success_stays_nonphysics(self):
        self.assertIn("Hull->SetStaticMesh(NewHull);", BODY)
        self.assertIn("ForwardBridge->SetStaticMesh(NewBridge);", BODY)
        self.assertIn("bBodyReviewApplied = true;", BODY)
        self.assertNotIn("SetCollisionEnabled", BODY)
        self.assertNotIn("SetSimulatePhysics", BODY)

    def test_editor_only_review_bypass_blocked_in_packages(self):
        self.assertIn("#if !WITH_EDITOR", BODY)
        early_branch = BODY.split("#if !WITH_EDITOR", 1)[1].split("#else", 1)[0]
        self.assertIn("return false;", early_branch)

    def test_orbiter_hold_covers_pending_and_applied_intent(self):
        for token in ("bUseAuthoredBodyReview", "bBodyReviewApplied", "bUseHullSilhouetteReview"):
            self.assertIn(token, REQUEST)
        self.assertIn("RequestedForm == EAureateWakeForm::Orbiter", REQUEST)
        self.assertIn("CurrentForm == EAureateWakeForm::Orbiter", REQUEST)

    def test_keep_four_mounts_and_two_struts_one_authority(self):
        self.assertIn("GetWingRootMountCount() const { return WingRootMounts.Num(); }", HEADER)
        self.assertIn("GetHydrofoilStrutCount() const { return HydrofoilStruts.Num(); }", HEADER)
        self.assertNotIn("WingRootSupports", HEADER)
        self.assertEqual(CPP.count("WingRootMounts.Add(Bracket);"), 1)

    def test_editor_refresh_lifecycle(self):
        build = CPP[
            CPP.index("void AAureateWakePreviewActor::OnConstruction("):
            CPP.index("void AAureateWakePreviewActor::RefreshHullSilhouetteReview()")
        ]
        self.assertIn("RefreshRootSupportReview();", build)
        self.assertIn("RefreshBodyReviewMeshes();", build)

    def test_native_rejections_are_registered(self):
        self.assertIn("Missing bridge fails body intake atomically", NATIVE)
        self.assertIn("Rejected body leaves hull mesh untouched", NATIVE)
        self.assertIn("Rejected body leaves bridge mesh untouched", NATIVE)
        self.assertIn("Conflicting review modes refused", NATIVE)
        self.assertIn("Body intent refuses Orbiter even with preview toggle", NATIVE)
        self.assertIn("Disabling review restores original mesh poses", NATIVE)


if __name__ == "__main__":
    unittest.main()
