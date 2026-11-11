#include "Misc/AutomationTest.h"
#include "TSTSSReviewShoreTravelSubsystem.h"
#include "TSTSSFirstWakeState.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSReviewShoreTravelGuardTest,
    "TSTSS.VerticalSlice.NativeSceneRouteStoryGate",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSReviewShoreTravelGuardTest::RunTest(const FString& Parameters)
{
    (void)Parameters;
    UTSTSSFirstWakeState* State = NewObject<UTSTSSFirstWakeState>();
    using Route = UTSTSSReviewShoreTravelSubsystem;
    const FString Prelude(TEXT("FirstWake_PreludeInteraction_V2"));
    TestFalse(TEXT("no transition before story starts"), Route::IsEligible(State, Prelude));
    TestTrue(TEXT("fixture: boarded ship"), State->Restore(
        true, ETSTSSFirstWakeBeat::BoardedAureateWake, 0));
    TestFalse(TEXT("unfinished inspections prohibit launch"), Route::IsEligible(State, Prelude));
    TestTrue(TEXT("fixture: checked engineering"), State->Restore(
        true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x07));
    TestEqual(TEXT("review launch moves first to sky"),
        Route::NextReviewMap(State, Prelude),
        FString(TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky")));
    TestFalse(TEXT("wrong source cannot initiate launch"),
        Route::IsEligible(State, TEXT("VS04_SplashdownSea")));
    TestTrue(TEXT("fixture: launched"), State->Restore(
        true, ETSTSSFirstWakeBeat::Launched, 0x07));
    TestFalse(TEXT("launch is not stable sea contact"),
        Route::IsEligible(State, TEXT("VS04_SplashdownSea")));
    TestTrue(TEXT("sky can proceed to real physical sea scene"),
        Route::IsEligible(State, TEXT("VS03_FirstWakeSky")));
    TestTrue(TEXT("fixture: sea contact only"), State->Restore(
        true, ETSTSSFirstWakeBeat::SeaContact, 0x07));
    TestFalse(TEXT("sea contact alone does not admit shanty"),
        Route::IsEligible(State, TEXT("VS04_SplashdownSea")));
    TestTrue(TEXT("fixture: physics established flotation"), State->Restore(
        true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07));
    TestEqual(TEXT("flotation admits the fuel shanty"),
        Route::NextReviewMap(State, TEXT("VS04_SplashdownSea")),
        FString(TEXT("/Game/TSTSS/Review/VerticalSlice/VS05_DenithFuelShanty")));
    TestFalse(TEXT("reserve check still required for shore"),
        Route::IsEligible(State, TEXT("VS05_DenithFuelShanty")));
    TestTrue(TEXT("fixture: reserves inspected"), State->Restore(
        true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 0x07));
    TestEqual(TEXT("shanty gate targets published native shore"),
        Route::NextReviewMap(State, TEXT("VS05_DenithFuelShanty")),
        FString(Route::ShorePackage()));
    TestFalse(TEXT("no direct Prelude-to-shore skip"),
        Route::IsEligible(State, Prelude));
    TestFalse(TEXT("no self-travel or early Lyra recruit"),
        Route::IsEligible(State, TEXT("L_VS06_ShoreMagicEnemyGear_Review")));
    return true;
}
#endif
