"""Private D3D11 Ender bone telemetry contracts (source-only; NOT art proof)."""
from pathlib import Path
import unittest
ROOT = Path(__file__).resolve().parents[1]
CPP = (ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
HEADER = (ROOT/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
def block():
    return CPP.split("if (FParse::Param(FCommandLine::Get(),\n                              TEXT(\"TSTSSPrivateEnderBoneAudit\")))",1)[1].split("// Only scoped review worlds advertise live interaction.",1)[0]
class PrivateBoneTelemetrySafetyTests(unittest.TestCase):
    def test_private_low_memory_game_only_and_explicit_diagnostic_flag(self):
        b=block()
        t=CPP.split("// Lower-RAM graphical fallback for the exact PRIVATE Ender review map.",1)[1].split("// Only scoped review worlds advertise live interaction.",1)[0]
        self.assertIn('IsPrivateEnderLowMemGameReview(World)',t)
        self.assertIn('GetClass()->GetName() == TEXT("BP_EnderLocomotionPreview_NONCANONICAL_C")',t)
        self.assertIn('World->GetNetMode() == NM_Standalone',t)
        self.assertIn('Scene == TEXT("FirstWake_PreludeInteraction_V5_VisualReview")',t)
        self.assertIn('TEXT("TSTSSPrivateEnderBoneAudit")',t)
        self.assertEqual(CPP.count('TEXT("TSTSSPrivateEnderBoneAudit")'),2)
        self.assertIn("TSTSS_ENDER_PRIVATE_BONE_AUDIT_FLAG",t)
        self.assertIn('TEXT("-TSTSSPrivateEnderBoneAudit")',t)
        self.assertIn('GetCharacterMovement()->IsMovingOnGround()',t)
        self.assertIn('#if WITH_EDITOR\n// The full Unreal Editor GUI',CPP)
    def test_all_152_bones_parent_edges_read_without_writes(self):
        b=block()
        for required in ('GetRefSkeleton()', 'GetParentIndex(Index)', 'GetRefBonePose()',
                         'GetBoneTransform(Index).GetLocation()', 'GetBoneTransform(ParentIndex).GetLocation()',
                         'FVector::Distance(A, B)', 'TSTSS_ENDER_PRIVATE_BONE_AUDIT_SAMPLE',
                         'TSTSS_ENDER_PRIVATE_BONE_AUDIT_BEGIN', 'TSTSS_ENDER_PRIVATE_BONE_AUDIT_END',
                         'render_eval=1 art_NOT_APPROVED', 'animation_REQUEST_ONLY art_NOT_APPROVED'):
            with self.subTest(required=required):self.assertIn(required,b)
        for forbidden in ('SaveGameToSlot(', 'OpenLevel(', 'SetActorLocation(',
                          'SetBone', 'SetSkeletalMeshAsset(', 'PlayAnimation(',
                          'SetAnimation(', 'Modify(', 'SetActorRotation(', 'SetMovementMode('):
            with self.subTest(forbidden=forbidden):self.assertNotIn(forbidden,b)
    def test_sampling_bounded_once_per_band_and_post_update(self):
        b=block()
        self.assertIn('EnderLowMemBoneAuditBandFrames >= 3',b)
        self.assertIn('PrimaryActorTick.TickInterval = 0.2f;',CPP)
        self.assertIn('(EnderLowMemBoneAuditSampledMask & BandBit) == 0',b)
        self.assertIn('EnderLowMemBoneAuditSampledMask |= BandBit',b)
        self.assertIn('EnderLowMemBoneAuditBandFrames < 60000',b)
        self.assertIn('1u << MotionBand',b)
        self.assertIn('uint8 EnderLowMemBoneAuditTrackedBand = 255;',HEADER)
        self.assertIn('uint16 EnderLowMemBoneAuditBandFrames = 0;',HEADER)
        self.assertIn('uint8 EnderLowMemBoneAuditSampledMask = 0;',HEADER)
        self.assertIn('TryEnderPIELocomotionPreview(MotionBand);',CPP)
    def test_mutated_guards_are_detected(self):
        b=block()
        for t in ('EnderLowMemBoneAuditBandFrames >= 3',
                  '(EnderLowMemBoneAuditSampledMask & BandBit) == 0',
                  'EnderLowMemBoneAuditSampledMask |= BandBit',
                  'GetParentIndex(Index)', 'TSTSS_ENDER_PRIVATE_BONE_AUDIT_SAMPLE'):
            with self.subTest(gate=t):self.assertNotIn(t,b.replace(t,'REMOVED_GUARD',1))
if __name__=="__main__":unittest.main()
