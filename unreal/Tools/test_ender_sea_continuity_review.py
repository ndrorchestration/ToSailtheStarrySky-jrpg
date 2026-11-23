"""Source-locked private sea observer custody: no authority to grant water beats.

Native water physics and actual Ender sea render remain separately gated.
"""
from pathlib import Path
import unittest

U=Path(__file__).resolve().parents[1]
SRC=(U/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf-8")
HEAD=(U/"Source/ToSailTheStarrySky/Public/TSTSSReviewShoreTravelSubsystem.h").read_text(encoding="utf-8")
EX=(U/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
QUEUE=SRC.split("bool UTSTSSReviewShoreTravelSubsystem::QueueShore(",1)[1].split(
    "bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(",1)[0]
ARR=SRC.split("bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(",1)[1].split(
    "bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(",1)[0]
SEA=SRC.split("bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInSeaReview(",1)[1]
BIND=EX.split("bool IsPrivateEnderSeaBinding(",1)[1].split(
    "bool IsPrivateEnderStandaloneAnimation(",1)[0]
APPEAR=EX.split("void ATSTSSExplorerCharacter::ApplyEnderSliceReviewAppearance()",1)[1].split(
    "void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(",1)[0]
CAMERA=EX.split("void ATSTSSExplorerCharacter::SetupFirstWakeThirdPersonReview(",1)[1].split(
    "void ATSTSSExplorerCharacter::",1)[0]
TICK=EX.split("void ATSTSSExplorerCharacter::Tick(",1)[1].split(
    "void ATSTSSExplorerCharacter::",1)[0]

class SeaCustody(unittest.TestCase):
    def test_two_independent_flags_and_earned_sky_beat(self):
        for t in ('TSTSSPrivateEnderSkyContinuityReview','TSTSSPrivateEnderSeaContinuityReview',
                  'SourceMap == SkyName && Destination == SeaPackage',
                  'ETSTSSFirstWakeBeat::Launched','State->AreInspectionsComplete()',
                  'World->WorldType == EWorldType::PIE',
                  'World->GetNetMode() == NM_Standalone',
                  '"_VS03_FirstWakeSky"', 'PrivateEnderPawnClassPath',
                  'Body->IsVisible() && Body->GetNumBones() >= 80'):
            self.assertIn(t,QUEUE)

    def test_distinct_single_use_arrival_is_not_sky_or_ship(self):
        for t in ('bPrivateEnderSeaArrivalReady = false;',
                  'bPrivateEnderSeaArrivalReady =',
                  'Target == SeaPackage',
                  '"_VS04_SplashdownSea"',
                  'State->GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched',
                  '!bPrivateEnderSeaArrivalReady'):
            self.assertIn(t,ARR)
        self.assertIn("bool bPrivateEnderSeaArrivalReady = false;",HEAD)

    def test_sea_binding_only_one_use_synchronous_spawn(self):
        for t in ('TSTSSPrivateEnderSkyContinuityReview',
                  'TSTSSPrivateEnderSeaContinuityReview',
                  '"_VS04_SplashdownSea"', 'BP_EnderLocomotionPreview_NONCANONICAL_C',
                  'IsPrivateEnderSeaSpawnInProgress()'):
            self.assertIn(t,BIND)
        self.assertIn("bool bPrivateEnderSeaSpawnInProgress = false;",HEAD)
        self.assertIn("bPrivateEnderSeaSpawnInProgress = true;",SEA)
        self.assertIn("bPrivateEnderSeaSpawnInProgress = false;",SEA)

    def test_spawn_requires_exact_earned_state_and_sea_map(self):
        for t in ('if (!bPrivateEnderSeaArrivalReady)', 'bPrivateEnderSeaArrivalReady = false;',
                  'PendingPrivateEnderClass = nullptr;',
                  'DefaultPawn->GetClass() != ATSTSSExplorerCharacter::StaticClass()',
                  'PC->GetPawn() != DefaultPawn',
                  'ETSTSSFirstWakeBeat::Launched','State->AreInspectionsComplete()',
                  'TSTSSPrivateEnderSeaContinuityReview',
                  'PrivateClass->IsChildOf(ATSTSSExplorerCharacter::StaticClass())',
                  'Ender->GetFirstWakeState()->Restore(',
                  'PC->Possess(Ender)', 'PC->GetPawn() != Ender'):
            self.assertIn(t,SEA)
        self.assertLess(SEA.index('bPrivateEnderSeaArrivalReady = false;'),
                        SEA.index('World->SpawnActor<ATSTSSExplorerCharacter>'))

    def test_observer_mode_after_possession_or_revert(self):
        self.assertLess(SEA.index('PC->Possess(Ender);'),
                        SEA.index('Ender->GetCharacterMovement()->SetMovementMode(MOVE_Flying);'))
        self.assertLess(SEA.index('SetMovementMode(MOVE_Flying);'),
                        SEA.index('DefaultPawn->Destroy();'))
        for t in ('MovementMode != MOVE_Flying','PC->Possess(DefaultPawn);',
                  'TSTSS_PRIVATE_ENDER_SEA_REBIND_HOLD observer_mode'):
            self.assertIn(t,SEA)

    def test_no_story_physics_or_map_mutation(self):
        for x in ('AdvanceTo(', 'AdvanceWaterBeat(', 'OpenLevel(', 'SaveGame',
                  'SetSimulatePhysics(', 'BindStory(', 'TeleportTo(',
                  'QueueShore(', 'SetActorLocation(', 'AddForce(', 'Reset()'):
            self.assertNotIn(x,SEA)
        self.assertIn('water_physics_UNTOUCHED', SEA)
        self.assertIn('no_piloting=1',SEA)

    def test_body_camera_only_one_use_private_sea(self):
        for scope in (APPEAR,CAMERA):
            self.assertIn('IsPrivateEnderSeaBinding(World, this)',scope)
            self.assertIn('Scene == TEXT("VS04_SplashdownSea") && bPrivateSeaBody',scope)
        self.assertIn('if (bPrivateSkyBody)',CAMERA)
        self.assertIn('if (bPrivateSeaBody)',CAMERA)

    def test_native_observation_real_measured_values(self):
        self.assertIn('Travel->TryResumePrivateEnderInSeaReview(this)',TICK)
        self.assertIn('TSTSS_PRIVATE_ENDER_SEA_OBSERVATION possessed=%d',TICK)
        for token in ('GetNumBones() >= 80','FollowCamera->IsActive()',
                      'PC->GetViewTarget() == this',
                      'MovementMode == MOVE_Flying',
                      'animation_NOT_VERIFIED visual_NOT_APPROVED'):
            self.assertIn(token,TICK)

    def test_original_default_water_adapter_unchanged(self):
        water=(U/"Source/ToSailTheStarrySky/Private/TSTSSWaterContactAdapter.cpp").read_text(encoding="utf-8")
        self.assertIn('if (Story != CurrentPlayerStory)',water)
        self.assertIn('BindStory(CurrentPlayerStory);',water)
        self.assertIn('Gate->Observe(DeltaSeconds, bActualImmersion, VerticalSpeed, Story);',water)

if __name__=="__main__":
    unittest.main()
