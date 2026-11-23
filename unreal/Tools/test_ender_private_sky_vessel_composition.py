"""Source safety checks for one opt-in, ship/Ender sky composition witness.
Render screenshots and native ship/idle receipts are separate gates.
"""
import unittest
from pathlib import Path
R=Path(__file__).resolve().parents[1]
CPP=(R/"Source/ToSailTheStarrySky/Private/TSTSSExplorerCharacter.cpp").read_text(encoding="utf8")
H=(R/"Source/ToSailTheStarrySky/Public/TSTSSExplorerCharacter.h").read_text(encoding="utf8")
VESSEL=(R/"Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp").read_text(encoding="utf8")
STATE=(R/"Source/ToSailTheStarrySky/Public/TSTSSFirstWakeState.h").read_text(encoding="utf8")
STORM=CPP.split("void ATSTSSExplorerCharacter::BeginPrivateSkyStormReview()",1)[1].split(
    "void ATSTSSExplorerCharacter::PrivateStormSecureLift()",1)[0]
COMPOSITION=STORM.split('TEXT("TSTSSPrivateSkyVesselCompositionReview")',1)[1].split(
    'TEXT("TSTSS_PRIVATE_SKY_STORM_START',1)[0]

class SkyVesselComposition(unittest.TestCase):
    def test_fail_closed_private_story_scope(self):
        self.assertIn('if (!IsPrivateSkyStormReviewWorld() || bPrivateSkyStormStarted)',STORM)
        self.assertIn('FParse::Param(FCommandLine::Get()',STORM)
        self.assertIn('FirstWakeState->IsReviewShipModeAuthorized(',COMPOSITION)
        self.assertIn('FName(TEXT("Skybourne"))',COMPOSITION)
        self.assertIn('GetReviewShipMode() const',STATE)
        self.assertIn('IsSeabourneRecoveryLocked()',STATE)
        self.assertIn('GetCurrentBeat() == ETSTSSFirstWakeBeat::Launched',CPP)

    def test_reuse_existing_four_wing_noncanonical_ship_only(self):
        for token in ('TActorIterator<AAureateWakePreviewActor>', '!bPreexistingVessel',
                      'SpawnActor<AAureateWakePreviewActor>',
                      'ESpawnActorCollisionHandlingMethod::AlwaysSpawn',
                      'ReviewParams.ObjectFlags |= RF_Transient',
                      'Vessel->BindReviewStory(FirstWakeState)',
                      'Vessel->GetCurrentForm() != EAureateWakeForm::Skyborne',
                      'Vessel->GetWingCount() != 4',
                      'Vessel->GetHydrofoilCount() != 2',
                      'Vessel->SetActorEnableCollision(false)',
                      'Vessel->Destroy()', 'Starbourne_locked=1'):
            self.assertIn(token,COMPOSITION)
        self.assertIn('for (int32 Index = 0; Index < 4; ++Index)',VESSEL)
        self.assertIn('SnapToForm(EAureateWakeForm::Skyborne)',VESSEL)

    def test_exact_private_idle_skeleton_and_root_motion_guard(self):
        for token in ('MM_Idle_EnderPreview_NONCANONICAL',
                      'Idle->GetSkeleton() ==',
                      'Body->GetSkeletalMeshAsset()->GetSkeleton()',
                      '!Idle->bEnableRootMotion',
                      'Body->GetAnimClass() == nullptr',
                      'Body->PlayAnimation(Idle, true)',
                      'Node->GetCurrentAsset() == Idle',
                      'brace_NOT_AUTHORED', 'unsafe_or_missing_private_clip'):
            self.assertIn(token,COMPOSITION)

    def test_no_world_or_pawn_transform_or_story_mutations(self):
        for token in ('AdvanceTo(', 'Restore(', 'SaveGame(', 'OpenLevel(',
                      'QueueShore(', 'SetActorLocation(', 'SetActorTransform(',
                      'SetWorldLocation(', 'SetWorldRotation(',
                      'SetMovementMode(', 'SetSimulatePhysics('):
            self.assertNotIn(token,COMPOSITION)
        self.assertIn('CameraBoom->TargetArmLength = 790.f',COMPOSITION)
        self.assertIn('CameraBoom->TargetOffset = FVector(0.f, 0.f, 75.f)',COMPOSITION)
        self.assertNotIn('bAllowOrbiterPreview = true',COMPOSITION)

    def test_unflagged_storm_weather_and_key_gates_unchanged(self):
        self.assertIn('Atmosphere->RequestWeather(ETSTSSWeather::Storm, 2.5f)',STORM)
        self.assertIn('Atmosphere->RequestTimeOfDay(19.0f, 3.0f)',STORM)
        self.assertIn('PrivateSkyStormResponseStage == 2',CPP)
        self.assertIn('TSTSS_PRIVATE_STORM_TRAVEL_HOLD R_then_T_required=1', (R/
            "Source/ToSailTheStarrySky/Private/TSTSSReviewShoreTravelSubsystem.cpp").read_text(encoding="utf8"))

if __name__=="__main__":unittest.main()
