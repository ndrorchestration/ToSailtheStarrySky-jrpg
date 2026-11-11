#include "Misc/AutomationTest.h"
#include "TSTSSReviewShoreTravelSubsystem.h"
#include "TSTSSFirstWakeState.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSReviewShoreTravelGuardTest,
    "TSTSS.VerticalSlice.ShoreTravelStoryGate",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSReviewShoreTravelGuardTest::RunTest(const FString& Parameters)
{
    (void)Parameters;
    UTSTSSFirstWakeState* State = NewObject<UTSTSSFirstWakeState>();
    const FString Prelude(TEXT("FirstWake_PreludeInteraction_V2"));
    TestFalse(TEXT("no opening gate before story starts"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(State, Prelude));
    TestTrue(TEXT("test fixture can restore prelaunch milestone"),
             State->Restore(true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestFalse(TEXT("launch is not proof of sea landing"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(State, Prelude));
    TestTrue(TEXT("test fixture can restore sea contact"),
             State->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07));
    TestFalse(TEXT("sea contact is not stable flotation"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(State, Prelude));
    TestTrue(TEXT("test fixture can restore stabilized landing"),
             State->Restore(true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    TestFalse(TEXT("reserve investigation is required before shore"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(State, Prelude));
    TestTrue(TEXT("test fixture can restore reserve investigation"),
             State->Restore(true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 0x07));
    TestTrue(TEXT("shore review permitted after reserve inspection"),
             UTSTSSReviewShoreTravelSubsystem::IsEligible(State, Prelude));
    TestFalse(TEXT("wrong source map may not offer shore shortcut"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(
                  State, TEXT("VS01_DenithHarbor")));
    TestFalse(TEXT("direct review shore load is not a valid source"),
              UTSTSSReviewShoreTravelSubsystem::IsEligible(
                  State, TEXT("L_VS06_ShoreMagicEnemyGear_Review")));
    TestEqual(TEXT("only the published independent review map is targeted"),
        FString(UTSTSSReviewShoreTravelSubsystem::ShorePackage()),
        FString(TEXT("/Game/TSTSS/Review/MultipathV1/L_VS06_ShoreMagicEnemyGear_Review")));
    return true;
}
#endif
