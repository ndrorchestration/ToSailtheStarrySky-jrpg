"""Source-only review of Ender VS03 private skeletal and camera binding.
Unreal native PIE proof and art approval remain distinct, unverified gates.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
P=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
S=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf8")
H=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSReviewShoreTravelSubsystem.h").read_text(encoding="utf8")
def between(text,a,b):
    return text.split(a,1)[1].split(b,1)[0]
GUARD=between(P,"bool IsPrivateEnderSkyBinding(", "bool IsPrivateEnderSeaBinding(")
APPEAR=between(P,"void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()", "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview")
CAMERA=between(P,"void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview", "void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview")
SKY=S.split("bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInSkyReview(",1)[1]

class EnderSkyVisualBinding(unittest.TestCase):
    def test_private_guard_requires_exact_class_and_opted_in_one_use_lease(self):
        for token in ('World->WorldType != EWorldType::PIE',
                      'World->GetNetMode() != NM_Standalone',
                      'TSTSSPrivateEnderSkyContinuityReview',
                      '"/Game/TSTSS/Review/VerticalSlice/UEDPIE_"',
                      '"_VS03_FirstWakeSky"',
                      'UGameplayStatics::GetCurrentLevelName(World, true) != TEXT("VS03_FirstWakeSky")',
                      'BP_EnderLocomotionPreview_NONCANONICAL_C',
                      'Travel->IsPrivateEnderSkySpawnInProgress()'):
            self.assertIn(token,GUARD)
        self.assertIn('bool bPrivateEnderSkySpawnInProgress = false;',H)
        self.assertIn('IsPrivateEnderSkySpawnInProgress() const',H)

    def test_helper_mutation_detection(self):
        critical=('World->WorldType != EWorldType::PIE',
                  'TSTSSPrivateEnderSkyContinuityReview',
                  'IsPrivateEnderSkySpawnInProgress()',
                  '"_VS03_FirstWakeSky"')
        def safe(source):
            return all(x in source for x in critical)
        self.assertTrue(safe(GUARD))
        for t in critical:
            with self.subTest(gate=t):
                self.assertFalse(safe(GUARD.replace(t, 'REMOVED_GUARD',1)))

    def test_visual_binding_includes_sky_only_with_private_lease(self):
        self.assertIn('const bool bPrivateSkyBody = IsPrivateEnderSkyBinding(World, this);',APPEAR)
        self.assertIn('!(Scene == TEXT("VS03_FirstWakeSky") && bPrivateSkyBody)',APPEAR)
        for token in ('EnderSliceReviewBody.LoadSynchronous()', 'GetRefSkeleton()',
                      'Body->SetSkeletalMeshAsset(Candidate)', 'Body->SetVisibility(true)',
                      'TSTSS_ENDER_SLICE_REVIEW_MESH_BOUND'):
            self.assertIn(token, APPEAR)
        self.assertNotIn('AdvanceTo(',APPEAR)

    def test_sky_camera_uses_skeletal_only_never_static_fallback(self):
        self.assertIn('const bool bPrivateSkyBody = IsPrivateEnderSkyBinding(World, this);',CAMERA)
        self.assertIn('!(Scene == TEXT("VS03_FirstWakeSky") && bPrivateSkyBody)',CAMERA)
        self.assertIn('bFirstWakeThirdPersonReview = true;',CAMERA)
        self.assertIn('if (bPrivateSkyBody)',CAMERA)
        self.assertIn('TSTSS_PRIVATE_ENDER_SKY_VIEW_HOLD no_visible_skeleton no_static_fallback=1',CAMERA)
        self.assertLess(CAMERA.index('if (bPrivateSkyBody)'),
                        CAMERA.index('constexpr const TCHAR* PackageRoot'))

    def test_sky_spawn_lease_bounds_beginplay_then_reset(self):
        before='bPrivateEnderSkySpawnInProgress = true;'
        spawn='World->SpawnActor<ATSTSSExplorerCharacter>'
        after='bPrivateEnderSkySpawnInProgress = false;'
        self.assertTrue(0 <= SKY.index(before) < SKY.index(spawn) < SKY.index(after))
        self.assertIn('GetSkeletalMeshAsset()',SKY)
        self.assertIn('Ender->GetMesh()->GetNumBones() < 80',SKY)
        self.assertIn('!Ender->GetMesh()->IsVisible()',SKY)
        self.assertLess(SKY.index('GetSkeletalMeshAsset()'),SKY.index('PC->Possess(Ender)'))
        self.assertIn('if (IsValid(Ender)) Ender->Destroy()',SKY)
        self.assertIn('DefaultPawn->Destroy();',SKY)
        self.assertIn('animation_NOT_VERIFIED art_NOT_APPROVED',SKY)

    def test_no_sky_airborne_animation_assertion(self):
        preview=between(P,'void ATSTSSExplorerCharacter::TryEnderPIELocomotionPreview',
                        'void ATSTSSExplorerCharacter::ToggleFirstWakeBokehReview')
        self.assertIn('Scene != TEXT("VS02_AureateInteriors")',preview)
        self.assertIn('IsMovingOnGround()',preview)
        self.assertNotIn('VS03_FirstWakeSky',preview)
        self.assertNotIn('SetSimulatePhysics(',SKY)
        self.assertNotIn('SaveGameToSlot(',SKY)

if __name__=="__main__":
    unittest.main()
