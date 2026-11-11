#include "Misc/AutomationTest.h"
#include "TSTSSAtmosphereDirector.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAtmospherePresetsTest,
    "TSTSS.Atmosphere.PresetsAndNightContinuity",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSAtmospherePresetsTest::RunTest(const FString& Parameters)
{
    for (int32 I = 0; I < 7; ++I)
    {
        const ETSTSSWeather Mode = static_cast<ETSTSSWeather>(I);
        const FTSTSSAtmosphereProfile P = ATSTSSAtmosphereDirector::ProfileFor(Mode, 23.0f);
        TestTrue(FString::Printf(TEXT("fog admitted %d"), I), P.FogDensity >= 0.0f && P.FogDensity <= 0.09f);
        TestTrue(FString::Printf(TEXT("cloud admitted %d"), I), P.CloudCoverage >= 0.0f && P.CloudCoverage <= 1.0f);
        TestTrue(FString::Printf(TEXT("rain admitted %d"), I), P.RainIntensity >= 0.0f && P.RainIntensity <= 1.0f);
        TestTrue(FString::Printf(TEXT("snow admitted %d"), I), P.SnowIntensity >= 0.0f && P.SnowIntensity <= 1.0f);
        TestFalse(FString::Printf(TEXT("no mixed precipitation %d"), I),
                  P.RainIntensity > 0.0f && P.SnowIntensity > 0.0f);
        TestTrue(FString::Printf(TEXT("wind positive %d"), I), P.WindSpeed > 0.0f);
    }
    const FTSTSSAtmosphereProfile A = ATSTSSAtmosphereDirector::ProfileFor(ETSTSSWeather::Clear, 23.0f);
    const FTSTSSAtmosphereProfile B = ATSTSSAtmosphereDirector::ProfileFor(ETSTSSWeather::Storm, 1.0f);
    const FTSTSSAtmosphereProfile Midnight = ATSTSSAtmosphereDirector::Interpolate(A, B, 0.5f);
    TestTrue(TEXT("cross-midnight shortest path"), Midnight.ClockHours < 0.01f);
    TestTrue(TEXT("storm crossfade fog between endpoints"),
             Midnight.FogDensity > A.FogDensity && Midnight.FogDensity < B.FogDensity);
    const FTSTSSAtmosphereProfile Before = ATSTSSAtmosphereDirector::Interpolate(A, B, -1.0f);
    const FTSTSSAtmosphereProfile After = ATSTSSAtmosphereDirector::Interpolate(A, B, 2.0f);
    TestEqual(TEXT("crossfade clamps lower"), Before.FogDensity, A.FogDensity);
    TestEqual(TEXT("crossfade clamps upper"), After.FogDensity, B.FogDensity);
    TestEqual(TEXT("clock wraps 25 to 1"), ATSTSSAtmosphereDirector::ProfileFor(
        ETSTSSWeather::Snow, 25.0f).ClockHours, 1.0f);
    return true;
}
#endif
