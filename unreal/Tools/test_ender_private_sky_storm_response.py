"""Source-bound private storm R/T -> K review, no release or pilot authority."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
P=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
H=(ROOT/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
R=(ROOT/"Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf8")
WORLD=P.split("bool ATSTSSExplorerCharacter::IsPrivateSkyStormReviewWorld() const",1)[1].split(
    "bool ATSTSSExplorerCharacter::IsPrivateSkyStormReviewComplete()",1)[0]
DONE=P.split("bool ATSTSSExplorerCharacter::IsPrivateSkyStormReviewComplete() const",1)[1].split(
    "void ATSTSSExplorerCharacter::BeginPrivateSkyStormReview()",1)[0]
INIT=P.split("void ATSTSSExplorerCharacter::BeginPrivateSkyStormReview()",1)[1].split(
    "void ATSTSSExplorerCharacter::PrivateStormSecureLift()",1)[0]
SECURE=P.split("void ATSTSSExplorerCharacter::PrivateStormSecureLift()",1)[1].split(
    "void ATSTSSExplorerCharacter::PrivateStormBraceForDescent()",1)[0]
BRACE=P.split("void ATSTSSExplorerCharacter::PrivateStormBraceForDescent()",1)[1].split(
    "void ATSTSSExplorerCharacter::ReviewShoreTravel()",1)[0]
QUEUE=R.split("bool UTSTSSReviewShoreTravelSubsystem::QueueShore(",1)[1].split(
    "bool UTSTSSReviewShoreTravelSubsystem::QueueOpticalInspection(",1)[0]
TICK=P.split("void ATSTSSExplorerCharacter::Tick(",1)[1].split(
    "void ATSTSSExplorerCharacter::EndPlay(",1)[0]

class StormResponsePrivateReview(unittest.TestCase):
    def test_exact_editor_pawn_and_real_story_only(self):
        for t in ('World->WorldType == EWorldType::PIE','NM_Standalone',
                  '"_VS03_FirstWakeSky"','"VS03_FirstWakeSky"',
                  'TSTSSPrivateSkyStormResponseReview',
                  'BP_EnderLocomotionPreview_NONCANONICAL_C',
                  'IsPlayerControlled()', 'bFirstWakeThirdPersonReview',
                  'ETSTSSFirstWakeBeat::Launched','FirstWakeState->AreInspectionsComplete()',
                  'Body->GetNumBones() >= 80','Body->IsVisible()'):
            self.assertIn(t,WORLD)

    def test_response_requires_order_and_explicit_duration(self):
        self.assertIn('bPrivateSkyStormStarted',DONE)
        self.assertIn('PrivateSkyStormResponseStage == 2',DONE)
        self.assertIn('>= 4.0f',DONE)
        self.assertIn('PrivateSkyStormResponseStage != 0',SECURE)
        self.assertIn('PrivateSkyStormResponseStage = 1;',SECURE)
        self.assertIn('PrivateSkyStormResponseStage != 1',BRACE)
        self.assertIn('PrivateSkyStormResponseStage = 2;',BRACE)
        for forbidden in ('AdvanceTo(', 'OpenLevel(', 'SaveGame', 'SetActorLocation(',
                          'SetSimulatePhysics(', 'AddForce(', 'SetActorTransform('):
            self.assertNotIn(forbidden,INIT+SECURE+BRACE+DONE)

    def test_real_player_actions_have_direct_key_bindings(self):
        self.assertIn('BindKey(EKeys::R, IE_Pressed',P)
        self.assertIn('BindKey(EKeys::T, IE_Pressed',P)
        self.assertIn('&ATSTSSExplorerCharacter::PrivateStormSecureLift',P)
        self.assertIn('&ATSTSSExplorerCharacter::PrivateStormBraceForDescent',P)
        for x in ('PrivateStormSecureLift();','PrivateStormBraceForDescent();',
                  'IsPrivateSkyStormReviewComplete() const'):
            self.assertIn(x,H)

    def test_k_queue_fail_closed_before_ticket(self):
        i=QUEUE.index('if (SourceMap == SkyName &&')
        guard=QUEUE[i:QUEUE.index('// K explicitly requests travel;',i)]
        for x in ('TSTSSPrivateSkyStormResponseReview',
                  'Ender->IsPrivateSkyStormReviewComplete()',
                  'TSTSS_PRIVATE_STORM_TRAVEL_HOLD',
                  'TSTSS_PRIVATE_STORM_TRAVEL_AUTHORIZED',
                  'return false;'):
            self.assertIn(x,guard)
        self.assertLess(i,QUEUE.index('State->AdvanceTo('))
        self.assertLess(i,QUEUE.index('PendingMapPackage = Destination;'))

    def test_storm_weather_uses_existing_director_preview_only(self):
        self.assertIn('TActorIterator<ATSTSSAtmosphereDirector>',INIT)
        self.assertIn('World->SpawnActor<ATSTSSAtmosphereDirector>',INIT)
        self.assertIn('Atmosphere->RequestWeather(ETSTSSWeather::Storm, 2.5f)',INIT)
        self.assertIn('Atmosphere->RequestTimeOfDay(19.0f, 3.0f)',INIT)
        self.assertIn('weather_requested=%d',INIT)
        self.assertIn('no_story_grant=1',INIT)
        self.assertIn('K locked',INIT)

    def test_key_probe_dispatches_controller_not_story(self):
        storm=TICK.split('if (IsPrivateSkyStormReviewWorld())',1)[1].split(
            '// An independent two-flag, one-use VS03 -> VS04 custody ticket',1)[0]
        for x in ('TSTSSPrivateStormInputProbe',
                  'TSTSS_PRIVATE_STORM_KEY_PROBE key=R',
                  'TSTSS_PRIVATE_STORM_KEY_PROBE key=T',
                  'PC->InputKey(FInputKeyEventArgs(',
                  'EKeys::R, IE_Pressed','EKeys::T, IE_Pressed'):
            self.assertIn(x,storm)
        self.assertNotIn('PrivateSkyStormResponseStage =',storm)
        self.assertNotIn('AdvanceTo(',storm)

    def test_existing_sky_k_stays_ungated_without_opt_in(self):
        key=TICK.split('const bool bEarnedSkyTransit =',1)[1].split('if (bEarnedShipDeparture',1)[0]
        self.assertIn('!FParse::Param(FCommandLine::Get()',key)
        self.assertIn('TSTSSPrivateSkyStormResponseReview',key)
        self.assertIn('IsPrivateSkyStormReviewComplete()',key)
        self.assertIn('World->GetTimeSeconds() >= 6.f',key)

    def test_early_k_negative_probe_releases_before_real_approval(self):
        storm=TICK.split('if (IsPrivateSkyStormReviewWorld())',1)[1].split(
            '// An independent two-flag, one-use VS03 -> VS04 custody ticket',1)[0]
        self.assertIn('TSTSS_PRIVATE_STORM_KEY_PROBE key=K_EARLY',storm)
        self.assertIn('EKeys::K, IE_Pressed',storm)
        self.assertIn('EKeys::K, IE_Released',storm)
        self.assertLess(storm.index('EKeys::K, IE_Pressed'),
                        storm.index('EKeys::K, IE_Released'))
        self.assertLess(storm.index('EKeys::K, IE_Released'),
                        storm.index('EKeys::R, IE_Pressed'))
        self.assertIn('bool bPrivateStormEarlyKProbeDispatched = false;',H)
        self.assertIn('bool bPrivateStormEarlyKProbeReleased = false;',H)

    def test_review_transient_no_save_or_canonical_state(self):
        for field in ('uint8 PrivateSkyStormResponseStage = 0;',
                      'float PrivateSkyStormStartWorldSeconds = 0.f;',
                      'bool bPrivateStormRProbeDispatched = false;',
                      'bool bPrivateStormTProbeDispatched = false;'):
            self.assertIn(field,H)
        self.assertNotIn('UPROPERTY(',H.split('bool bPrivateLaunchKDispatched = false;',1)[1].split(
            'uint64 HilltoniaFlyerGeneration',1)[0])

if __name__=="__main__":
    unittest.main()
