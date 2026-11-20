"""Review-only standalone Ender binding contract; not art or animation approval."""
from pathlib import Path
import unittest

CPP = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")

def block(src, start, end):
    return src.split(start, 1)[1].split(end, 1)[0]

def admitted(src):
    try:
        h = block(src, "bool IsPrivateEnderStandaloneBinding(", "\nvoid ApplyCoastalRecoveryReviewSignage")
        b = block(src, "void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", "\nvoid ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview")
    except IndexError:
        return False
    guards = (
        "World->WorldType == EWorldType::Game",
        "World->GetNetMode() == NM_Standalone",
        'TEXT("TSTSSPrivateEnderLowMemReview")',
        "World->GetOutermost()->GetName() ==",
        'TEXT("/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/FirstWake_PreludeInteraction_V5_VisualReview")',
        'Pawn->GetClass()->GetPathName() ==',
        'TEXT("/Game/TSTSS/Review/Characters/EnderRetarget_NONCANONICAL/BP_EnderLocomotionPreview_NONCANONICAL.BP_EnderLocomotionPreview_NONCANONICAL_C")',
    )
    return all(g in h for g in guards) and all(g in b for g in (
        "IsPrivateEnderStandaloneBinding(World, this)",
        "(World->WorldType != EWorldType::PIE && !bPrivateStandalone)",
        "EnderSliceReviewBody.IsNull()",
        "Body->SetSkeletalMeshAsset(Candidate)",
    ))

class StandaloneBindingTests(unittest.TestCase):
    def test_explicit_exact_private_world_and_pawn(self):
        self.assertTrue(admitted(CPP))

    def test_each_admission_guard_is_required(self):
        for token in ("World->WorldType == EWorldType::Game",
                      "World->GetNetMode() == NM_Standalone",
                      'TEXT("TSTSSPrivateEnderLowMemReview")',
                      "World->GetOutermost()->GetName() ==",
                      "Pawn->GetClass()->GetPathName() ==",
                      "IsPrivateEnderStandaloneBinding(World, this)"):
            with self.subTest(token=token):
                self.assertFalse(admitted(CPP.replace(token, "REMOVED_GATE", 1)))

    def test_does_not_enable_animation_or_change_story(self):
        h = block(CPP, "bool IsPrivateEnderStandaloneBinding(", "\nvoid ApplyCoastalRecoveryReviewSignage")
        for forbidden in ("PlayAnimation(", "OpenLevel(", "SaveGameToSlot(", "SetActorLocation(", "AdvanceTo("):
            self.assertNotIn(forbidden, h)
        preview = block(CPP, "void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview", "\nvoid ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview")
        self.assertIn("World->WorldType != EWorldType::PIE", preview)

if __name__ == "__main__":
    unittest.main()
