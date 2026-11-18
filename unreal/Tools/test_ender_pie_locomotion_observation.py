"""Source-only guard for bounded Ender PIE possession/locomotion observations.

These assertions do not run Unreal, prove skeletal deformation, verify an AnimBP,
certify appearance, or assert actual in-game playback.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT / "Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
HDR = (ROOT / "Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf-8")


def observation(src):
    tick = src.split("void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)", 1)[1].split(
        "void ATSTSSExplorerCharacter::EndPlay(", 1
    )[0]
    return tick.split("// Ender v0.1 PIE locomotion observation:", 1)[1].split(
        "// Only scoped review worlds advertise live interaction.", 1
    )[0]


def is_bounded(src):
    tick = src.split("void ATSTSSExplorerCharacter::Tick(float DeltaSeconds)", 1)[1].split(
        "// Ender v0.1 PIE locomotion observation:", 1
    )[0]
    block = observation(src)
    return "IsPlayerControlled()" in tick and all(token in block for token in (
        "bReviewNamespace",
        "World->WorldType == EWorldType::PIE",
        "World->GetNetMode() == NM_Standalone",
        "bFirstWakeThirdPersonReview",
        'Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',
        'Scene == TEXT("VS02_AureateInteriors")',
        "SkeletalBody->IsRegistered()",
        "SkeletalBody->GetSkeletalMeshAsset()",
        "SkeletalBody->GetNumBones() > 0",
        "SkeletalBody->IsVisible()",
        "if (!bEnderPIEPossessionLogged)",
        "if (MotionBand != LastEnderPIEMotionBand)",
        "TSTSS_ENDER_PIE_POSSESSION_SAMPLE",
        "TSTSS_ENDER_PIE_VELOCITY_BAND",
        "animation_NOT_VERIFIED art_NOT_APPROVED",
    ))


class EnderPIELocomotionObservationSourceTests(unittest.TestCase):
    def test_only_existing_possessed_standalone_pie_review_pawn(self):
        self.assertTrue(is_bounded(CPP))
        self.assertIn("uint8 LastEnderPIEMotionBand = 255;", HDR)
        self.assertIn("bool bEnderPIEPossessionLogged = false;", HDR)
        self.assertIn("#if WITH_EDITOR", CPP.split(
            "// Ender v0.1 PIE locomotion observation:", 1
        )[0])

    def test_observation_reports_velocity_not_claimed_animations(self):
        block = observation(CPP)
        for required in ("GetVelocity().Size2D()", "SpeedCmS < 10.f",
                         "SpeedCmS < 300.f", "stationary", "walking_speed",
                         "running_speed", "anim_instance_present=%d",
                         "GetAnimInstance() != nullptr", "grounded=%d",
                         "animation_NOT_VERIFIED art_NOT_APPROVED"):
            with self.subTest(required=required):
                self.assertIn(required, block)
        for denied in ("SetSkeletalMeshAsset(", "SetAnimation(", "SetAnimInstanceClass(",
                       "AdvanceTo(", "SaveGameToSlot(", "OpenLevel(", "TeleportTo(",
                       "SetActorLocation(", "SetMovementMode("):
            with self.subTest(denied=denied):
                self.assertNotIn(denied, block)

    def test_mutations_on_all_essential_gates_fail_closed(self):
        baseline = observation(CPP)
        for gate in ("World->WorldType == EWorldType::PIE",
                     "World->GetNetMode() == NM_Standalone",
                     "bFirstWakeThirdPersonReview",
                     'Scene == TEXT("VS02_AureateInteriors")',
                     "SkeletalBody->IsVisible()",
                     "if (!bEnderPIEPossessionLogged)",
                     "if (MotionBand != LastEnderPIEMotionBand)",
                     "animation_NOT_VERIFIED art_NOT_APPROVED"):
            with self.subTest(gate=gate):
                altered = CPP.replace(baseline, baseline.replace(gate, "/* missing gate */"), 1)
                self.assertFalse(is_bounded(altered))


if __name__ == "__main__":
    unittest.main()
