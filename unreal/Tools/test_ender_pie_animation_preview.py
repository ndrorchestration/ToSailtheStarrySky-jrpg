"""Source-only fail-closed contract for opt-in Ender PIE idle/walk/run preview.

This never executes Unreal or certifies runtime animation, fit, deformation,
foot planting, native compiled code, asset licensing, or creator approval.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")


def preview(src):
    return src.split("void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)", 1)[1].split(
        "void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()", 1
    )[0]


def guarded(src):
    b = preview(src)
    return all(s in b for s in (
        "!bEnableEnderPIELocomotionPreview", "!IsPlayerControlled()",
        "bFirstWakeThirdPersonReview", "MotionBand > 2",
        "World->WorldType != EWorldType::PIE",
        "World->GetNetMode() != NM_Standalone",
        'TEXT("/Game/TSTSS/Review/")',
        'Scene != TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
        'Scene != TEXT("VS02_AureateInteriors")',
        "EnderSliceReviewBody.IsNull()",
        "Body->GetSkeletalMeshAsset() != EnderSliceReviewBody.Get()",
        "Body->IsRegistered()", "Body->IsVisible()",
        "GetCharacterMovement()->IsMovingOnGround()",
        "if (!bEnderPIEAnimPreviewChecked)",
        "Body->GetAnimClass() != nullptr",
        "Body->GetAnimationMode() == EAnimationMode::AnimationCustomMode",
        "EnderPIEIdleAnimation.IsNull()",
        "EnderPIEWalkAnimation.IsNull()",
        "EnderPIERunAnimation.IsNull()",
        "Idle->GetSkeleton() != BoundSkeleton",
        "Walk->GetSkeleton() != BoundSkeleton",
        "Run->GetSkeleton() != BoundSkeleton",
        "Idle->bEnableRootMotion",
        "Walk->bEnableRootMotion",
        "Run->bEnableRootMotion",
        "Body->GetAnimationMode() != EAnimationMode::AnimationSingleNode",
        "if (LastEnderPIEAnimBand == MotionBand)",
        "Body->PlayAnimation(Next, true)",
        "playback_NOT_VERIFIED", "deformation_NOT_VERIFIED",
    ))


class EnderPIELocomotionPreviewTests(unittest.TestCase):
    def test_default_denied_and_editor_only_transient_fields(self):
        self.assertIn("class UAnimSequence;", HDR)
        self.assertIn("bool bEnableEnderPIELocomotionPreview = false;", HDR)
        self.assertIn("#if WITH_EDITORONLY_DATA", HDR)
        self.assertIn("UPROPERTY(Transient)", HDR)
        for name in ("Idle", "Walk", "Run"):
            self.assertIn(f"TSoftObjectPtr<UAnimSequence> EnderPIE{name}Animation", HDR)
            self.assertIn(f"TObjectPtr<UAnimSequence> EnderPIE{name}Loaded", HDR)
        self.assertIn("#include \"Animation/AnimSequence.h\"", CPP)
        self.assertTrue(guarded(CPP))

    def test_transition_requires_grounded_genuine_controlled_pawn(self):
        tick = CPP.split("void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)", 1)[1].split(
            "void ATSTSSExplorerCharacter::EndPlay(", 1
        )[0]
        self.assertIn("IsPlayerControlled()", tick)
        self.assertIn("bReviewNamespace", tick)
        self.assertIn("World->WorldType == EWorldType::PIE", tick)
        self.assertIn("World->GetNetMode() == NM_Standalone", tick)
        self.assertIn("bFirstWakeThirdPersonReview", tick)
        self.assertIn("if (bSkeletalVisible)", tick)
        self.assertIn("GetCharacterMovement()->IsMovingOnGround()", tick)
        self.assertIn("TryEnderPIELocomotionPreview(MotionBand);", tick)
        for denied in ("Body->PlayAnimation(", "SetAnimation(", "SaveGameToSlot(",
                       "SetActorLocation(", "OpenLevel(", "AdvanceTo("):
            self.assertNotIn(denied, tick)
        for denied in ("SaveGameToSlot(", "OpenLevel(", "AdvanceTo(",
                       "SetActorLocation(", "SetMovementMode(", "SetActorRotation("):
            self.assertNotIn(denied, preview(CPP))

    def test_missing_any_gate_is_caught_by_contract(self):
        block = preview(CPP)
        for gate in (
            "!bEnableEnderPIELocomotionPreview",
            "!IsPlayerControlled()",
            "bFirstWakeThirdPersonReview",
            "World->WorldType != EWorldType::PIE",
            "World->GetNetMode() != NM_Standalone",
            "Body->GetSkeletalMeshAsset() != EnderSliceReviewBody.Get()",
            "GetCharacterMovement()->IsMovingOnGround()",
            "Body->GetAnimClass() != nullptr",
            "EnderPIEIdleAnimation.IsNull()",
            "EnderPIEWalkAnimation.IsNull()",
            "EnderPIERunAnimation.IsNull()",
            "Idle->GetSkeleton() != BoundSkeleton",
            "Walk->GetSkeleton() != BoundSkeleton",
            "Run->GetSkeleton() != BoundSkeleton",
            "Idle->bEnableRootMotion",
            "Walk->bEnableRootMotion",
            "Run->bEnableRootMotion",
            "Body->GetAnimationMode() != EAnimationMode::AnimationSingleNode",
            "Body->PlayAnimation(Next, true)",
            "playback_NOT_VERIFIED",
        ):
            with self.subTest(gate=gate):
                altered = CPP.replace(block, block.replace(gate, "/* removed */"), 1)
                self.assertFalse(guarded(altered))


if __name__ == "__main__":
    unittest.main()
