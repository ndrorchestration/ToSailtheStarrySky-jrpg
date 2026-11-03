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
    TestEqual(TEXT("Pre-load timeline accumulated 1.75 seconds"),
        SameBeatGate->GetStableContactSeconds(), 1.75f);
    const uint64 GenerationBeforeSameBeatRestore = SameBeatStory->GetRestoreGeneration();
    TestTrue(TEXT("Restore the same SeaContact snapshot into the same object"),
        SameBeatStory->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07));
    TestEqual(TEXT("Successful restore advances generation"),
        SameBeatStory->GetRestoreGeneration(), GenerationBeforeSameBeatRestore + 1);
    TestFalse(TEXT("Same-beat restore cannot inherit pre-load settling time"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Same-beat restore remains at SeaContact"),
        SameBeatStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Only post-load stability is counted"),
        SameBeatGate->GetStableContactSeconds(), 0.25f);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Fresh post-load samples remain below two seconds"),
            SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Fresh post-load duration is 1.75 seconds"),
        SameBeatGate->GetStableContactSeconds(), 1.75f);
    TestTrue(TEXT("Flotation requires two fresh post-load seconds"),
        SameBeatGate->Observe(0.25f, true, 0.f, SameBeatStory));
    TestEqual(TEXT("Same-beat restore eventually confirms flotation"),
        SameBeatStory->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);

    // Accumulate old-timeline evidence, then quickload into the SAME Story and
    // Gate while hull overlap remains true. No caller-side Gate->Reset().
    // Quarter-second samples make the two-second boundary exact.
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Old timeline has not settled yet"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Old timeline accumulated stability"), Gate->GetStableContactSeconds(), 1.5f);
    const uint64 GenerationBeforeRejectedRestore = Story->GetRestoreGeneration();
    TestFalse(TEXT("Incomplete engineering snapshot is rejected"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x03));
    TestEqual(TEXT("Failed restore preserves contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Failed restore preserves accumulated stability"), Gate->GetStableContactSeconds(), 1.5f);
    TestEqual(TEXT("Rejected restore does not advance generation"),
        Story->GetRestoreGeneration(), GenerationBeforeRejectedRestore);
    if (!TestTrue(TEXT("Rewind existing story to Launched"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07))) return false;

    TestFalse(TEXT("First post-rewind sample cannot confirm flotation"),
        Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Rewind immediately reacquires SeaContact"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Rewind discards all old stable duration"), Gate->GetStableContactSeconds(), 0.25f);
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Insufficient fresh stability cannot complete"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Only fresh samples count toward stability"), Gate->GetStableContactSeconds(), 1.75f);
    TestEqual(TEXT("Still SeaContact before two fresh seconds"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestTrue(TEXT("Two fresh stable seconds confirm flotation"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Restored contact can eventually confirm flotation"),
        Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::FlotationConfirmed);
    TestEqual(TEXT("Completion uses exactly two fresh seconds"), Gate->GetStableContactSeconds(), 2.f);
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
    return true;
}

#endif
