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

    // Accumulate old-timeline evidence, then quickload into the SAME Story and
    // Gate while hull overlap remains true. No caller-side Gate->Reset().
    // Quarter-second samples make the two-second boundary exact.
    for (int32 Index = 0; Index < 6; ++Index)
        TestFalse(TEXT("Old timeline has not settled yet"), Gate->Observe(0.25f, true, 0.f, Story));
    TestEqual(TEXT("Old timeline accumulated stability"), Gate->GetStableContactSeconds(), 1.5f);
    TestFalse(TEXT("Incomplete engineering snapshot is rejected"),
        Story->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x03));
    TestEqual(TEXT("Failed restore preserves contact"), Story->GetCurrentBeat(), ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Failed restore preserves accumulated stability"), Gate->GetStableContactSeconds(), 1.5f);
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
