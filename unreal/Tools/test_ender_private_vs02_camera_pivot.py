"""Fail-closed source checks for the opt-in private Ender interior camera pivot."""
from pathlib import Path
import unittest

CPP = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
BODY = CPP.split("void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(UWorld* World)", 1)[1].split(
    "void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(", 1)[0]

def scoped(text):
    return all(token in text for token in (
        'Scene == TEXT("VS02_AureateInteriors")',
        'FParse::Param(FCommandLine::Get(), TEXT("TSTSSPrivateEnderCameraPivotReview"))',
        'BP_EnderLocomotionPreview_NONCANONICAL_C',
        'bInteriors ? (bPrivateEnderCameraPivotReview ? 75.f : 45.f) : 35.f'))

class EnderCameraPivotReviewTest(unittest.TestCase):
    def test_private_scope(self):
        self.assertTrue(scoped(BODY))
        self.assertIn('World->WorldType != EWorldType::PIE', BODY)
        self.assertIn('GetNetMode() != NM_Standalone', BODY)

    def test_negative_scope_mutations(self):
        for token in (
            'Scene == TEXT("VS02_AureateInteriors")',
            'TSTSSPrivateEnderCameraPivotReview',
            'BP_EnderLocomotionPreview_NONCANONICAL_C',
            'bInteriors ? (bPrivateEnderCameraPivotReview ? 75.f : 45.f) : 35.f'):
            with self.subTest(token=token):
                self.assertFalse(scoped(BODY.replace(token, 'REMOVED_GATE', 1)))

    def test_camera_collision_and_maps_unchanged(self):
        self.assertNotIn('bDoCollisionTest = false', BODY)
        self.assertNotIn('SetActorLocation(', BODY)
        self.assertNotIn('SaveGame', BODY)
        self.assertIn('CameraBoom->TargetArmLength = bInteriors ? 340.f : 480.f;', BODY)
        self.assertIn('CameraBoom->SocketOffset = FVector(0.f, 48.f, 12.f);', BODY)

if __name__ == "__main__":
    unittest.main()
