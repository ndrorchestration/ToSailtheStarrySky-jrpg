#include "Misc/AutomationTest.h"
#include "TSTSSWaterLandingGate.h"
#include "TSTSSFirstWakeState.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSWaterLandingRestoreTest,
    "TSTSS.FirstWake.WaterLandingRestore",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSWaterLandingRestoreTest::RunTest(const FString& Parameters)
{
    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* Gate = NewObject<UTSTSSWaterLandingGate>();
    if (!TestTrue(TEXT("Restore saved SeaContact"), Story->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07))) return false;
    TestFalse(TEXT("First stable sample does not complete"), Gate->Observe(0.1f, true, 0.f, Story));
    TestEqual(TEXT("Still at SeaContact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("First qualifying sample anchors an interval but credits no prior time"),
        Gate->GetStableContactSeconds(), 0.f);
    for (int32 Index=0; Index<9; ++Index) Gate->Observe(0.1f, true, 0.f, Story);
    TestFalse(TEXT("Loss of overlap resets stability"), Gate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("No premature flotation"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);

    // Same-beat quickload: the saved story state is unchanged, but transient
    // settling evidence accumulated after the save must not survive the restore.
    UTSTSSFirstWakeState* SameBeatStory = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* SameBeatGate = NewObject<UTSTSSWaterLandingGate>();
    if (!TestTrue(TEXT("Restore launched state for same-beat scenario"),
        SameBeatStory->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07))) return false;
    TestFalse(TEXT("First same-beat sample records contact only"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Same-beat snapshot is SeaContact"),
        SameBeatStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Pre-load timeline remains below two seconds"),
            SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Pre-load timeline has 1.5 directly observed seconds"),
        SameBeatGate->GetStableContactSeconds(), 1.5f);
    const uint64 GenerationBeforeSameBeatRestore = SameBeatStory->GetRestoreGeneration();
    TestTrue(TEXT("Restore the same SeaContact snapshot into the same object"),
        SameBeatStory->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07));
    TestEqual(TEXT("Successful restore advances generation"),
        SameBeatStory->GetRestoreGeneration(), GenerationBeforeSameBeatRestore + 1);
    TestFalse(TEXT("Same-beat restore cannot inherit pre-load settling time"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Same-beat restore remains at SeaContact"),
        SameBeatStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("No pre-load interval is credited to the first post-load sample"),
        SameBeatGate->GetStableContactSeconds(), 0.f);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Fresh post-load samples remain below two seconds"),
            SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Fresh post-load observed duration is 1.5 seconds"),
        SameBeatGate->GetStableContactSeconds(), 1.5f);
    TestFalse(TEXT("Eight calm samples have only 1.75 observed seconds"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestTrue(TEXT("Nine calm samples span two observed seconds after restore"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Same-beat restore eventually confirms flotation"),
        SameBeatStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);

    // Accumulate old-timeline evidence, then quickload into the SAME Story and
    // Gate while hull overlap remains true. No caller-side Gate->Reset().
    // Quarter-second samples make the two-second boundary exact.
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Old timeline has not settled yet"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Old timeline has only observed stable intervals"), Gate->GetStableContactSeconds(), 1.25f);
    const uint64 GenerationBeforeRejectedRestore = Story->GetRestoreGeneration();
    TestFalse(TEXT("Incomplete engineering snapshot is rejected"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x03));
    TestEqual(TEXT("Failed restore preserves contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Failed restore preserves accumulated stability"), Gate->GetStableContactSeconds(), 1.25f);
    TestEqual(TEXT("Rejected restore does not advance generation"),
        Story->GetRestoreGeneration(), GenerationBeforeRejectedRestore);
    if (!TestTrue(TEXT("Rewind existing story to Launched"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07))) return false;

    TestFalse(TEXT("First post-rewind sample cannot confirm flotation"),
        Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Rewind immediately reacquires SeaContact"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Rewind discards all old stable duration"), Gate->GetStableContactSeconds(), 0.f);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Insufficient fresh stability cannot complete"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Only observed fresh sample intervals count"), Gate->GetStableContactSeconds(), 1.5f);
    TestEqual(TEXT("Still SeaContact before two fresh seconds"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestFalse(TEXT("Eight samples are only 1.75 seconds of observed intervals"),
        Gate->Observe(0.25f, true, 0.f, Story));
    TestTrue(TEXT("Nine samples span two observed seconds"),
        Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Restored contact can eventually confirm flotation"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);
    TestEqual(TEXT("Completion uses exactly two fresh seconds"), Gate->GetStableContactSeconds(), 2.f);

    // A full Reset() may be followed by a complete new Prelude before the
    // water adapter observes another frame. Prior SeaContact/settling state
    // must never leak into this new timeline in the same Story and Gate.
    UTSTSSFirstWakeState* RestartedStory = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* RestartedGate = NewObject<UTSTSSWaterLandingGate>();
    if (!TestTrue(TEXT("Seed old SeaContact before full restart"),
        RestartedStory->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07))) return false;
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Old restart timeline not yet floating"),
            RestartedGate->Observe(0.25f, true, 0.f, RestartedStory));
    TestEqual(TEXT("Old restart timeline accumulated 1.25 observed seconds"),
        RestartedGate->GetStableContactSeconds(), 1.25f);
    const uint64 GenerationBeforeReset = RestartedStory->GetRestoreGeneration();
    RestartedStory->Reset();
    TestEqual(TEXT("Full Reset invalidates cached contact generation"),
        RestartedStory->GetRestoreGeneration(), GenerationBeforeReset + 1);
    TestFalse(TEXT("Restart clears started flag"), RestartedStory->HasStarted());
    TestEqual(TEXT("Restart clears inspection mask"), RestartedStory->GetInspectionMask(), uint8(0));

    TestTrue(TEXT("Restart discovers flyer"),
        RestartedStory->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Restart hires Ionia"),
        RestartedStory->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired));
    TestTrue(TEXT("Restart boards Aureate Wake"),
        RestartedStory->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestTrue(TEXT("Restart inspects lift"),
        RestartedStory->InspectStation(ETSTSSInspectionStation::Lift));
    TestTrue(TEXT("Restart inspects pressure"),
        RestartedStory->InspectStation(ETSTSSInspectionStation::Pressure));
    TestTrue(TEXT("Restart inspects reserve"),
        RestartedStory->InspectStation(ETSTSSInspectionStation::Reserve));
    TestTrue(TEXT("Restart signs off engineering"),
        RestartedStory->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Restart launches only after engineering"),
        RestartedStory->AdvanceTo(ETSTSSFirstWakeBeat::Launched));
    TestFalse(TEXT("First post-reset contact cannot complete flotation"),
        RestartedGate->Observe(0.25f, true, 0.f, RestartedStory));
    TestEqual(TEXT("New timeline genuinely reacquires SeaContact"),
        RestartedStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("New timeline first calm frame credits no prior time"),
        RestartedGate->GetStableContactSeconds(), 0.f);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("New timeline has insufficient stable duration"),
            RestartedGate->Observe(0.25f, true, 0.f, RestartedStory));
    TestEqual(TEXT("New timeline has precisely 1.5 observed seconds"),
        RestartedGate->GetStableContactSeconds(), 1.5f);
    TestFalse(TEXT("Eight samples cannot count as two observed seconds"),
        RestartedGate->Observe(0.25f, true, 0.f, RestartedStory));
    TestTrue(TEXT("New timeline requires nine clean samples for two observed seconds"),
        RestartedGate->Observe(0.25f, true, 0.f, RestartedStory));
    TestEqual(TEXT("Full restart eventually confirms fresh flotation"),
        RestartedStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);
    return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSWaterLandingNegativePathsTest,
    "TSTSS.FirstWake.WaterLandingNegativePaths",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSWaterLandingNegativePathsTest::RunTest(const FString& Parameters)
{
    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* Gate = NewObject<UTSTSSWaterLandingGate>();
    if (!TestTrue(TEXT("Restore Launched"), Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07))) return false;

    TestFalse(TEXT("No collision cannot advance"), Gate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("Still launched"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::Launched);
    TestFalse(TEXT("Bad delta rejected"), Gate->Observe(0.3f, true, 0.f, Story));
    TestEqual(TEXT("Bad delta does not record contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::Launched);

    TestFalse(TEXT("Physical contact registers but not immediate flotation"),
        Gate->Observe(0.1f, true, 150.f, Story));
    TestEqual(TEXT("Contact recorded"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    for (int32 Index = 0; Index < 15; ++Index)
        Gate->Observe(0.1f, true, 90.f, Story);
    TestEqual(TEXT("Fast motion never confirms flotation"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);

    for (int32 Index = 0; Index < 10; ++Index)
        Gate->Observe(0.1f, true, 0.f, Story);
    TestFalse(TEXT("Moving hull resets settled sample"),
        Gate->Observe(0.1f, true, 90.f, Story));
    for (int32 Index = 0; Index < 10; ++Index)
        Gate->Observe(0.1f, true, 0.f, Story);
    TestEqual(TEXT("Incomplete stability must not confirm"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);

    Gate->Reset();
    TestFalse(TEXT("No overlap after reset"), Gate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("Reset preserves story contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);

    // Exactly 25 cm/s is permitted, but the historically observed 25.231
    // cm/s preceding flotation is not. Neither that unqualified frame nor
    // its elapsed delta may count toward a new two-second window.
    UTSTSSFirstWakeState* ThresholdStory = NewObject<UTSTSSFirstWakeState>();
    UTSTSSWaterLandingGate* ThresholdGate = NewObject<UTSTSSWaterLandingGate>();
    if (!TestTrue(TEXT("Boundary story restores launched state"),
        ThresholdStory->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07))) return false;
    for (int32 Index = 0; Index < 8; ++Index)
        TestFalse(TEXT("Eight exact-limit samples cannot confirm flotation"),
            ThresholdGate->Observe(0.25f, true, 25.f, ThresholdStory));
    TestEqual(TEXT("Eight exact-limit samples span only 1.75 observed seconds"),
        ThresholdGate->GetStableContactSeconds(), 1.75f);
    TestFalse(TEXT("25.231 cm/s is above the stability speed limit"),
        ThresholdGate->Observe(0.25f, true, 25.231f, ThresholdStory));
    TestEqual(TEXT("Above-threshold 25.231 cm/s clears stability"),
        ThresholdGate->GetStableContactSeconds(), 0.f);
    for (int32 Index = 0; Index < 8; ++Index)
        TestFalse(TEXT("Eight new limit-speed samples remain below two seconds"),
            ThresholdGate->Observe(0.25f, true, 25.f, ThresholdStory));
    TestTrue(TEXT("Nine fresh exact-limit samples finally confirm flotation"),
        ThresholdGate->Observe(0.25f, true, 25.f, ThresholdStory));
    TestEqual(TEXT("Boundary trace requires two fresh witnessed seconds"),
        ThresholdGate->GetStableContactSeconds(), 2.f);
    return true;
}

#endif
