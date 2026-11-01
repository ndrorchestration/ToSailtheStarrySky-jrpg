"""Source-only contracts for the optional Aureate Wake hull silhouette study.

These assertions do not replace a native UE 5.8 compile, material review,
mesh collision analysis, or D3D12 screenshots.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "Source" / "ToSailTheStarrySky"
CPP = (SOURCE / "Private" / "AureateWakePreviewActor.cpp").read_text(encoding="utf-8")
HEADER = (SOURCE / "Public" / "AureateWakePreviewActor.h").read_text(encoding="utf-8")
NATIVE_TEST = (SOURCE / "Private" / "Tests" / "AureateWakePreviewNativeTests.cpp").read_text(encoding="utf-8")


class AureateHullCanopySourceContracts(unittest.TestCase):
    def test_opt_in_only_preserves_old_visuals(self):
        self.assertIn("bool bUseHullSilhouetteReview = false;", HEADER)
        self.assertIn("Hull->SetVisibility(!bShowPrimitiveStudy);", CPP)
        self.assertIn("ForwardBridge->SetVisibility(!bShowPrimitiveStudy);", CPP)
        self.assertIn("Section->SetVisibility(bShowPrimitiveStudy);", CPP)
        self.assertIn("Rib->SetVisibility(bShowPrimitiveStudy);", CPP)

    def test_four_surfaces_and_geodesic_study_frame(self):
        # Exactly four study parts: mid-hull, bow, stern, open deck.
        self.assertEqual(len(re.findall(r'AddHullSection\(TEXT\("Review', CPP)), 4)
        self.assertIn("const int32 RingSegments = 8;", CPP)
        self.assertEqual(CPP.count("AddCanopyRib("), 5)
        self.assertIn("GetHullSilhouetteSectionCount() const", HEADER)
        self.assertIn("GetCanopyFramePieceCount() const", HEADER)
        self.assertIn("GetCanopyFramePieceCount(), 40", NATIVE_TEST)

    def test_study_uses_noncolliding_primitives(self):
        self.assertIn("Component->SetCollisionEnabled(ECollisionEnabled::NoCollision);", CPP)
        self.assertIn("/Engine/BasicShapes/Sphere.Sphere", CPP)
        self.assertIn("SetupPreviewMesh(Section, Mesh);", CPP)
        self.assertIn("SetupPreviewMesh(Rib, Shape);", CPP)
        self.assertIn("SetupPreviewMesh(CanopyShell, CurvedShape);", CPP)

    def test_no_fake_glass_without_authored_material(self):
        self.assertIn("OptionalCanopyGlassMaterial", HEADER)
        self.assertIn("bShowPrimitiveStudy && OptionalCanopyGlassMaterial != nullptr", CPP)
        self.assertIn("CanopyShell->SetVisibility(bShowGlass);", CPP)
        self.assertIn("CanopyShell->SetCastShadow(false);", CPP)

    def test_actor_keeps_four_original_wings_and_two_foils(self):
        self.assertIn("for (int32 Index = 0; Index < 4; ++Index)", CPP)
        self.assertIn("for (int32 Index = 0; Index < 2; ++Index)", CPP)
        self.assertIn("Wings.Add(Wing);", CPP)
        self.assertIn("Hydrofoils.Add(Foil);", CPP)
        self.assertIn("GetWingCount(), 4", NATIVE_TEST)
        self.assertIn("GetHydrofoilCount(), 2", NATIVE_TEST)

    def test_orbiter_authored_transition_remains_blocked(self):
        self.assertIn("(bUseRootPivotedWingPose && (RequestedForm == EAureateWakeForm::Orbiter", CPP)
        self.assertIn("CurrentForm == EAureateWakeForm::Orbiter))", CPP)
        self.assertIn("Hull review does not authorize Orbiter", NATIVE_TEST)

    def test_editor_review_transition_is_packaged_fail_closed(self):
        match = re.search(
            r'bool AAureateWakePreviewActor::FinishOrdinaryPreviewTransitionForReview\(\)\s*\{(?P<body>.*?)\n\}',
            CPP, re.DOTALL
        )
        self.assertIsNotNone(match)
        body = match.group("body")
        self.assertIn("#if WITH_EDITOR", body)
        self.assertIn("#else", body)
        self.assertIn("return false;", body.split("#else", 1)[1].split("#endif", 1)[0])

    def test_no_new_story_or_buoyancy_authority(self):
        self.assertNotIn('#include "TSTSSFirstWakeState.h"', CPP)
        self.assertNotIn('#include "TSTSSWaterLandingGate.h"', CPP)
        self.assertNotIn('SetSimulatePhysics(true)', CPP)


if __name__ == "__main__":
    unittest.main()
