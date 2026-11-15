#include "Misc/AutomationTest.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSReviewShoreTravelSubsystem.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSFirstWakeEngineRoomReboardTest,
    "TSTSS.FirstWake.EngineRoomReboardAuthority",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSFirstWakeEngineRoomReboardTest::RunTest(const FString& Parameters)
{
    using Route = UTSTSSReviewShoreTravelSubsystem;
    UTSTSSFirstWakeState* State = NewObject<UTSTSSFirstWakeState>();
    if (!TestNotNull(TEXT("Engine room route has a state"), State)) return false;
    const FString Harbor(TEXT("FirstWake_PreludeInteraction_V5_VisualReview"));
    const FString Legacy(TEXT("FirstWake_PreludeInteraction_V2"));
    const FString Ship(TEXT("VS02_AureateInteriors"));
    const FString ShipPackage(TEXT("/Game/TSTSS/Review/VerticalSlice/VS02_AureateInteriors"));
    const FString SkyPackage(TEXT("/Game/TSTSS/Review/VerticalSlice/VS03_FirstWakeSky"));

    TestFalse(TEXT("Unstarted cannot board ship"), Route::IsEligible(State, Harbor));
    if (!TestTrue(TEXT("Flyer"), State->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered))) return false;
    if (!TestTrue(TEXT("Hire Ionia"), State->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired))) return false;
    TestFalse(TEXT("Hiring does not board automatically"), Route::IsEligible(State, Harbor));
    if (!TestTrue(TEXT("Board ship"), State->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake))) return false;
    TestEqual(TEXT("Boarding opens engine room before checks"), Route::NextReviewMap(State, Harbor), ShipPackage);
    TestFalse(TEXT("Legacy V2 still rejects early travel"), Route::IsEligible(State, Legacy));
    TestFalse(TEXT("Ship cannot launch before all checks"), Route::IsEligible(State, Ship));
    TestFalse(TEXT("Signoff refused without inspections"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked));
    if (!TestTrue(TEXT("LIFT accepted"), State->InspectStation(ETSTSSInspectionStation::Lift))) return false;
    TestEqual(TEXT("One inspection bit stays one"), State->GetInspectionMask(), static_cast<uint8>(0x01));
    TestEqual(TEXT("Partial earned review route retains ship destination"), Route::NextReviewMap(State, Harbor), ShipPackage);
    TestFalse(TEXT("LIFT alone does not launch"), Route::IsEligible(State, Ship));
    if (!TestTrue(TEXT("Pressure accepted"), State->InspectStation(ETSTSSInspectionStation::Pressure))) return false;
    TestFalse(TEXT("Two checks still deny launch"), Route::IsEligible(State, Ship));
    if (!TestTrue(TEXT("Reserve accepted"), State->InspectStation(ETSTSSInspectionStation::Reserve))) return false;
    TestFalse(TEXT("All inspections without signoff still deny launch"), Route::IsEligible(State, Ship));
    if (!TestTrue(TEXT("In-room signoff accepted"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked))) return false;
    TestEqual(TEXT("Only after signoff may ship launch"), Route::NextReviewMap(State, Ship), SkyPackage);
    TestEqual(TEXT("V5 completed legacy saves may still arrive ship first"), Route::NextReviewMap(State, Harbor), ShipPackage);
    TestFalse(TEXT("Unrelated V4 scene does not grant launch"), Route::IsEligible(State, TEXT("FirstWake_PreludeInteraction_V4_VisualReview")));
    TestFalse(TEXT("Direct sea scene cannot launch"), Route::IsEligible(State, TEXT("VS04_SplashdownSea")));
    TestFalse(TEXT("Starbourne still denied"), State->IsReviewShipModeAuthorized(FName(TEXT("Starbourne"))));
    TestFalse(TEXT("Missing inspection evidence rejected on restore"),
        State->Restore(true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x00));
    return true;
}
#endif
