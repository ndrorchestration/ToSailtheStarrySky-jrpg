"""Source guards for explicitly opted-in private standalone animation review.

Source checks are not native playback, a keyboard test, or art approval.
"""
from pathlib import Path
import unittest

CPP = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")


def section(src, start, end):
    return src.split(start, 1)[1].split(end, 1)[0]


def contract(src):
    try:
        helper = section(src, "bool IsPrivateEnderStandaloneAnimation(", "\nvoid ApplyCoastalRecoveryReviewSignage")
        tick = section(src, "// Private standalone Ender animation observation:",
                       "// Only scoped review worlds advertise live interaction.")
        preview = section(src, "void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview(uint8 MotionBand)",
                          "void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview()")
        return all(token in helper for token in (
            'TEXT("TSTSSPrivateEnderAnimationReview")',
            'IsPrivateEnderStandaloneBinding(World, Pawn)',
            'IsPrivateEnderStandaloneShip(World)',
            'Pawn->GetClass()->GetPathName()',
            'BP_EnderLocomotionPreview_NONCANONICAL_C',
        )) and all(token in tick for token in (
            'IsPrivateEnderStandaloneAnimation(World, this)',
            'IsPlayerControlled()', 'GetVelocity().Size2D()',
            'GetCharacterMovement()->IsMovingOnGround()',
            'TryEnderPIELocomotionPreview(MotionBand)',
        )) and all(token in preview for token in (
            '!bEnableEnderPIELocomotionPreview',
            'World->WorldType != EWorldType::PIE',
            '!IsPrivateEnderStandaloneAnimation(World, this)',
            'Body->GetSkeletalMeshAsset() != EnderSliceReviewBody.Get()',
            'CurrentNode->GetCurrentAsset() != PreviouslyRequested',
            'ERootMotionMode::IgnoreRootMotion',
        ))
    except IndexError:
        return False


class PrivateStandaloneAnimationContract(unittest.TestCase):
    def test_private_standalone_animation_is_explicit_and_scoped(self):
        self.assertTrue(contract(CPP), "Standalone animation path and guards are not yet present")

    def test_missing_guards_are_detected(self):
        self.assertTrue(contract(CPP))
        for token in ('TSTSSPrivateEnderAnimationReview',
                      'IsPrivateEnderStandaloneBinding(World, Pawn)',
                      'IsPrivateEnderStandaloneShip(World)',
                      'BP_EnderLocomotionPreview_NONCANONICAL_C',
                      'IsPlayerControlled()',
                      'GetCharacterMovement()->IsMovingOnGround()',
                      'CurrentNode->GetCurrentAsset() != PreviouslyRequested',
                      'ERootMotionMode::IgnoreRootMotion'):
            with self.subTest(token=token):
                self.assertFalse(contract(CPP.replace(token, "REMOVED_GUARD")))


if __name__ == "__main__":
    unittest.main()
