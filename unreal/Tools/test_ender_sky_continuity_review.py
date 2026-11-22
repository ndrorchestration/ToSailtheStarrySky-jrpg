"""Source-only fail-closed review contract for Ender's optional VS02-to-sky pawn custody.
Runtime/native visual acceptance requires separate Unreal evidence.
"""
from pathlib import Path
import unittest

U = Path(__file__).resolve().parents[1]
CPP = (U/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf-8")
H = (U/"Source/ToSailTheStarrySky/Public/TSTSSReviewShoreTravelSubsystem.h").read_text(encoding="utf-8")
EXP = (U/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf-8")
QUEUE = CPP.split("bool UTSTSSReviewShoreTravelSubsystem::QueueShore(",1)[1].split(
    "bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(",1)[0]
ARRIVE = CPP.split("bool UTSTSSReviewShoreTravelSubsystem::ConsumeShoreArrival(",1)[1].split(
    "bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInShipRoom(",1)[0]
SKY = CPP.split("bool UTSTSSReviewShoreTravelSubsystem::TryResumePrivateEnderInSkyReview(",1)[1]
TICK = EXP.split("void ATSTSSExplorerCharacter::Tick(",1)[1].split(
    "void ATSTSSExplorerCharacter::",1)[0]

class EnderSkyContinuityReviewContract(unittest.TestCase):
    def test_default_route_requires_explicit_pie_flag_and_exact_map(self):
        for token in ('TSTSSPrivateEnderSkyContinuityReview',
                      'World->WorldType == EWorldType::PIE',
                      'World->GetNetMode() == NM_Standalone',
                      '"/Game/TSTSS/Review/VerticalSlice/UEDPIE_"',
                      'SourceMap == ShipName && Destination == SkyPackage',
                      'ETSTSSFirstWakeBeat::Launched',
                      'State->AreInspectionsComplete()',
                      'PrivateEnderPawnClassPath'):
            self.assertIn(token,QUEUE)

    def test_one_use_earned_arrival_exact_class_and_review_namespace(self):
        for token in ('bPrivateEnderSkyArrivalReady = false',
                      'bRestored && World->WorldType == EWorldType::PIE',
                      'Target == SkyPackage',
                      '_VS03_FirstWakeSky',
                      'State->AreInspectionsComplete()',
                      'PendingPrivateEnderClass.Get()->GetPathName() == PrivateEnderPawnClassPath'):
            self.assertIn(token, ARRIVE)
        self.assertIn('if (!bPrivateEnderArrivalReady && !bPrivateEnderSkyArrivalReady)', ARRIVE)

    def test_resume_consumes_ticket_before_spawn_and_checks_possession(self):
        token='bPrivateEnderSkyArrivalReady = false;'
        self.assertIn('if (!bPrivateEnderSkyArrivalReady)', SKY)
        self.assertLess(SKY.index(token), SKY.index('World->SpawnActor<ATSTSSExplorerCharacter>'))
        for required in ('World->WorldType != EWorldType::PIE',
                         'TSTSSPrivateEnderSkyContinuityReview',
                         'DefaultPawn->GetClass() != ATSTSSExplorerCharacter::StaticClass()',
                         'PC->GetPawn() != DefaultPawn',
                         'ETSTSSFirstWakeBeat::Launched',
                         '!PrivateClass->GetPathName().Equals(',
                         'PrivateClass->IsChildOf(ATSTSSExplorerCharacter::StaticClass())',
                         'PC->Possess(Ender)', 'PC->GetPawn() != Ender',
                         'Ender->GetFirstWakeState()->Restore(',
                         'DefaultPawn->Destroy()'):
            self.assertIn(required, SKY)

    def test_only_observer_flight_not_ship_physics_or_story(self):
        self.assertIn('SetMovementMode(MOVE_Flying)', SKY)
        self.assertIn('no_piloting=1 animation_NOT_VERIFIED art_NOT_APPROVED', SKY)
        for forbidden in ('AdvanceTo(', 'AdvanceWaterBeat(', 'OpenLevel(',
                          'SaveGameToSlot(', 'SetSimulatePhysics(', 'TeleportTo('):
            self.assertNotIn(forbidden, SKY)
        self.assertIn('TryResumePrivateEnderInShipRoom', TICK)
        self.assertIn('TryResumePrivateEnderInSkyReview', TICK)
        self.assertIn('bool bPrivateEnderSkyArrivalReady = false;', H)

    def test_observer_mode_set_only_after_successful_possession(self):
        # Native 2026-11-22 review observed the sky pawn possessed but not
        # flying: ACharacter::Restart can reset the pre-possess movement mode.
        # Do not accept a falling private pawn over an observer-only sky map.
        possess=SKY.index("PC->Possess(Ender);")
        flying=SKY.index("Ender->GetCharacterMovement()->SetMovementMode(MOVE_Flying);")
        self.assertLess(possess, flying)
        self.assertLess(flying, SKY.index("DefaultPawn->Destroy();"))
        self.assertIn("Ender->GetCharacterMovement()->MovementMode != MOVE_Flying", SKY)
        self.assertIn("TSTSS_PRIVATE_ENDER_SKY_REBIND_HOLD observer_mode", SKY)
        self.assertLess(SKY.index("PC->GetPawn() != Ender"), flying)

    def test_original_unflagged_sky_input_probe_remains_observer_only(self):
        probe = EXP.split("// Review-only native K input, not a simulated launch/landing grant.",1)[1].split(
            "// Explicitly flagged editor-built -game title preview:",1)[0]
        self.assertIn('GetClass() == ATSTSSExplorerCharacter::StaticClass()',probe)
        self.assertIn('World->GetTimeSeconds() >= 6.f',probe)
        # The original default-observer predicate remains present, while
        # the private Ender branch is separately gated by explicit opt-in.
        self.assertIn('bEarnedPrivateSkeletalSkyTransit',probe)
        self.assertIn('TSTSSPrivateEnderSkyContinuityReview',probe)
        self.assertIn('FirstWakeState->AreInspectionsComplete()',probe)
        self.assertIn('GetMesh()->GetNumBones() >= 80',probe)

if __name__ == "__main__":
    unittest.main()
