#include "Misc/AutomationTest.h"
#include "TSTSSAtmosphereDirector.h"
#include "TSTSSFirstWakeState.h"
#include "Review/TSTSSPresentationCoordinatorSubsystem.h"

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

    // Reuse this registered native identity: do not change the locked 35-test
    // automation inventory for a review-only, non-runtime-admitted feature.
    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    if (!TestNotNull(TEXT("Review-only presentation test story object"), Story))
    {
        return false;
    }
    int32 AcceptedSignals = 0;
    const FDelegateHandle Observer = Story->OnAcceptedChange().AddLambda(
        [&AcceptedSignals]() { ++AcceptedSignals; });
    using EPM = ETSTSSPresentationMoment;
    const auto Resolve = [Story](EPM Moment, const FString& Map,
                                ETSTSSWeather Weather, bool bReduced = false,
                                bool bClarity = false)
    {
        return UTSTSSPresentationCoordinatorSubsystem::ResolveForReview(
            Story, Moment, Map, Weather, bReduced, bClarity);
    };

    TestFalse(TEXT("Engine focus denied before actual boarding"),
              Resolve(EPM::EngineInspection, TEXT("VS02_AureateInteriors"),
                      ETSTSSWeather::Clear).bEligible);
    TestTrue(TEXT("Flyer genuinely accepted"), Story->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Ionia genuinely hired"), Story->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired));
    TestTrue(TEXT("Ship genuinely boarded"), Story->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestEqual(TEXT("Exactly three accepted story transitions notified"), AcceptedSignals, 3);
    const FTSTSSPresentationIntent Engine = Resolve(
        EPM::EngineInspection, TEXT("UEDPIE_0_VS02_AureateInteriors"),
        ETSTSSWeather::Clear);
    TestTrue(TEXT("Boarded engine inspection gains review focus intent"), Engine.bEligible);
    TestTrue(TEXT("Engine focus intent available"), Engine.bAllowCinematicFocus);
    TestTrue(TEXT("Authored focus rack intent available"), Engine.bAllowFocusRack);
    TestFalse(TEXT("Authoring intent does not require deep focus"), Engine.bRequireDeepFocus);
    TestEqual(TEXT("Expected external lighting key"), Engine.LightingLookId, FName(TEXT("engineering")));
    TestEqual(TEXT("Semantic sound intent only"), Engine.AudioIntentId,
              FName(TEXT("mechanical_hum_gauge_resonance")));
    TestEqual(TEXT("Focus shot must match source binding"), Engine.ShotId,
              FName(TEXT("FW03_Engine_Inspection")));
    TestEqual(TEXT("Merely resolving does not change story"), Story->GetCurrentBeat(),
              ETSTSSFirstWakeBeat::BoardedAureateWake);
    TestEqual(TEXT("Merely resolving does not inspect equipment"), Story->GetInspectionMask(),
              static_cast<uint8>(0u));
    TestFalse(TEXT("Wrong native map denied"), Resolve(
        EPM::EngineInspection, TEXT("VS01_DenithHarbor"),
        ETSTSSWeather::Clear).bEligible);
    TestFalse(TEXT("Spoofed map suffix cannot authorize presentation"), Resolve(
        EPM::EngineInspection, TEXT("FakeVS02_AureateInteriors"),
        ETSTSSWeather::Clear).bEligible);
    TestFalse(TEXT("Malformed PIE map prefix cannot authorize presentation"), Resolve(
        EPM::EngineInspection, TEXT("UEDPIE_abc_VS02_AureateInteriors"),
        ETSTSSWeather::Clear).bEligible);
    TestFalse(TEXT("Blizzard cannot silently use unsupported engineering look"), Resolve(
        EPM::EngineInspection, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Blizzard).bEligible);
    TestFalse(TEXT("Engine awakening needs actual three inspections"), Resolve(
        EPM::EngineAwakening, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Clear).bEligible);
    TestTrue(TEXT("Actual lift inspection"), Story->InspectStation(ETSTSSInspectionStation::Lift));
    TestTrue(TEXT("Actual pressure inspection"), Story->InspectStation(ETSTSSInspectionStation::Pressure));
    TestTrue(TEXT("Actual reserve inspection"), Story->InspectStation(ETSTSSInspectionStation::Reserve));
    TestEqual(TEXT("All three inspections each notify accepted visual observers"), AcceptedSignals, 6);
    const uint64 ObservedGeneration = Story->GetRestoreGeneration();
    TestTrue(TEXT("Current accepted source snapshot remains valid"),
        UTSTSSPresentationCoordinatorSubsystem::MatchesStorySnapshot(
            Story, ObservedGeneration, true,
            ETSTSSFirstWakeBeat::BoardedAureateWake, 0x07));
    TestFalse(TEXT("Rejected water milestone does not advance or notify"), Story->AdvanceTo(
        ETSTSSFirstWakeBeat::SeaContact));
    TestEqual(TEXT("Rejected milestone cannot emit false visual event"), AcceptedSignals, 6);
    TestTrue(TEXT("Engine response becomes a visual request only after inspections"), Resolve(
        EPM::EngineAwakening, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Clear).bEligible);
    const FTSTSSPresentationIntent Reduced = Resolve(
        EPM::EngineInspection, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Clear, true, false);
    TestTrue(TEXT("Reduced motion retains scene intent"), Reduced.bEligible);
    TestFalse(TEXT("Reduced motion removes focus rack"), Reduced.bAllowFocusRack);
    TestTrue(TEXT("Reduced motion enforces clarity"), Reduced.bRequireDeepFocus);
    const FTSTSSPresentationIntent Clarity = Resolve(
        EPM::EngineInspection, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Storm, false, true);
    TestFalse(TEXT("Gameplay clarity overrides optical focus"), Clarity.bAllowCinematicFocus);
    TestTrue(TEXT("Gameplay clarity leaves story state unchanged"),
             Story->GetCurrentBeat() == ETSTSSFirstWakeBeat::BoardedAureateWake);
    TestFalse(TEXT("Night-sky look must not invent shore-night lighting"), Resolve(
        EPM::NightSkyWonder, TEXT("VS06_SplashdownShore"),
        ETSTSSWeather::Clear).bEligible);
    Story->Reset();
    TestEqual(TEXT("Reset invalidation reaches visual observer"), AcceptedSignals, 7);
    TestFalse(TEXT("Reset invalidates previously observed story snapshot"),
        UTSTSSPresentationCoordinatorSubsystem::MatchesStorySnapshot(
            Story, ObservedGeneration, true,
            ETSTSSFirstWakeBeat::BoardedAureateWake, 0x07));
    TestFalse(TEXT("Reset clears engine presentation eligibility"), Resolve(
        EPM::EngineInspection, TEXT("VS02_AureateInteriors"),
        ETSTSSWeather::Clear).bEligible);
    TestTrue(TEXT("Valid restore of observed inspections accepted"), Story->Restore(
        true, ETSTSSFirstWakeBeat::BoardedAureateWake, 0x07));
    TestEqual(TEXT("Restore invalidates dependent presentation"), AcceptedSignals, 8);
    Story->OnAcceptedChange().Remove(Observer);

    return true;
}
#endif
