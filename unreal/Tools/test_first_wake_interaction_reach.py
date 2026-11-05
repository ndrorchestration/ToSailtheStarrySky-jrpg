"""Source-contract regression for third-person interaction ray origin and reach."""
from pathlib import Path
import math
import unittest

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT/"Source/ToSailTheStarrySky/Public"
PRIVATE = ROOT/"Source/ToSailTheStarrySky/Private"


class CameraReachSourceTests(unittest.TestCase):
    def test_default_boom_exceeds_old_camera_only_ray(self):
        pawn=(0.0, 0.0, 130.0)
        camera=(-360.0, 0.0, 130.0)
        target=(190.0, 0.0, 130.0)
        reach=300.0
        old_length=reach
        new_length=math.dist(camera, pawn)+reach
        self.assertGreater(math.dist(camera,target),old_length)
        self.assertLess(math.dist(camera,target),new_length)
        self.assertLessEqual(math.dist(pawn,target),reach)
        self.assertEqual(new_length,660.0)

    def test_native_code_applies_two_separate_geometry_gates(self):
        source=(PRIVATE/"TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
        self.assertIn('TSTSSInteractionReach::GetCameraTraceLength(',source)
        self.assertIn('TSTSSInteractionReach::IsInsidePlayerReach(',source)
        self.assertIn('LineTraceSingleByChannel',source)
        self.assertIn('Milestone->TryActivate(FirstWakeState)',source)
        self.assertNotIn('FollowCamera->GetForwardVector() * FMath::Max(0.f, InteractionDistance)',source)

    def test_reach_guard_rejects_nonfinite_and_outside_pawn_range(self):
        header=(PUBLIC/"TSTSSInteractionReach.h").read_text(encoding="utf-8")
        self.assertIn("CameraOffset + PlayerReach",header)
        self.assertIn("IsFinite(PlayerReach)",header)
        self.assertIn("PawnLocation.ContainsNaN()",header)
        self.assertIn("ImpactPoint.ContainsNaN()",header)
        self.assertIn("FVector::DistSquared(PawnLocation, ImpactPoint)",header)
        self.assertIn("FMath::Square(PlayerReach)",header)

    def test_native_editor_suite_declares_regression(self):
        tests=(PRIVATE/"Tests/TSTSSInteractionReachTests.cpp").read_text(encoding="utf-8")
        verifier=(ROOT/"Tools/Verify-Unreal.ps1").read_text(encoding="utf-8")
        self.assertIn("TSTSS.FirstWake.InteractionCameraBoomReach",tests)
        self.assertIn("TSTSS.FirstWake.InteractionCameraBoomReach",verifier)
        for text in ("Past 300 cm", "Nonfinite impact", "Exactly 300 cm"):
            self.assertIn(text,tests)


if __name__=="__main__":
    unittest.main()
