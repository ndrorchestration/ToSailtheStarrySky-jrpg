#include "Misc/AutomationTest.h"
#include "TSTSSReviewGrounding.h"
#include <limits>

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSReviewDockReturnTest,
    "TSTSS.FirstWake.ReviewDockReturnBoundaries",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSReviewDockReturnTest::RunTest(const FString& Parameters)
{
    using namespace TSTSSReviewGrounding;
    const FVector Anchor(0.f, 0.f, 160.f);
    const FVector Drop(800.f, 100.f, -300.f);
    TestTrue(TEXT("Harbor drop rescued"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), true, true, Drop, Anchor));
    TestTrue(TEXT("Prelude drop rescued"), ShouldRecover(true, TEXT("FirstWake_PreludeInteraction_V2"), true, true, Drop, Anchor));
    TestTrue(TEXT("Shore drop rescued"), ShouldRecover(true, TEXT("VS06_SplashdownShore"), true, true, Drop, Anchor));
    TestTrue(TEXT("Shore enemy gear review rescued"), ShouldRecover(true, TEXT("L_VS06_ShoreMagicEnemyGear_Review"), true, true, Drop, Anchor));
    TestFalse(TEXT("A sea fall is not auto-corrected"), ShouldRecover(true, TEXT("VS04_SplashdownSea"), true, true, Drop, Anchor));
    TestFalse(TEXT("Sky scene not auto-corrected"), ShouldRecover(true, TEXT("VS03_FirstWakeSky"), true, true, Drop, Anchor));
    TestFalse(TEXT("Production map not auto-corrected"), ShouldRecover(true, TEXT("GameMap"), true, true, Drop, Anchor));
    TestFalse(TEXT("Shipping or unrelated runtime has no override"), ShouldRecover(false, TEXT("VS01_DenithHarbor"), true, true, Drop, Anchor));
    TestFalse(TEXT("No ground anchor cannot teleport"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), false, true, Drop, Anchor));
    TestFalse(TEXT("Grounded player cannot teleport"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), true, false, Drop, Anchor));
    TestFalse(TEXT("Small step is not a fall"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), true, true, FVector(0.f,0.f,-230.f), Anchor));
    TestFalse(TEXT("Threshold equality does not rescue"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), true, true, FVector(0.f,0.f,-240.f), Anchor));
    TestFalse(TEXT("NaN coordinates rejected"), ShouldRecover(true, TEXT("VS01_DenithHarbor"), true, true, FVector(0.f, 0.f, std::numeric_limits<float>::quiet_NaN()), Anchor));
    return true;
}
#endif
