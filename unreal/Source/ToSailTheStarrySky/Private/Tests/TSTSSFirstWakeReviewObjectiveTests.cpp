#include "Misc/AutomationTest.h"
#include "TSTSSFirstWakeState.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSFirstWakeReviewObjectiveTest,
    "TSTSS.FirstWake.ReviewObjectivesAreReadOnly",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSFirstWakeReviewObjectiveTest::RunTest(const FString& Parameters)
{
    UTSTSSFirstWakeState* State = NewObject<UTSTSSFirstWakeState>();
    if (!TestNotNull(TEXT("Transient review state exists"), State)) return false;

    TestEqual(TEXT("Initial read-only objective"),
        State->GetReviewObjectiveText(), FString(TEXT("Find Ionia's flyer")));
    TestFalse(TEXT("Objective query cannot start the story"), State->HasStarted());

    if (!TestTrue(TEXT("Discover flyer"), State->AdvanceTo(ETSTSSFirstWakeBeat::FlyerDiscovered))) return false;
    TestEqual(TEXT("Ionia is next"), State->GetReviewObjectiveText(),
        FString(TEXT("Speak with Captain Ionia")));
    if (!TestTrue(TEXT("Hire Ionia"), State->AdvanceTo(ETSTSSFirstWakeBeat::IoniaHired))) return false;
    TestEqual(TEXT("Boarding is next"), State->GetReviewObjectiveText(),
        FString(TEXT("Board the Aureate Wake")));
    if (!TestTrue(TEXT("Board ship"), State->AdvanceTo(ETSTSSFirstWakeBeat::BoardedAureateWake))) return false;
    TestEqual(TEXT("First incomplete inspection shown"), State->GetReviewObjectiveText(),
        FString(TEXT("Inspect the levitation lift")));

    if (!TestTrue(TEXT("Inspect lift"), State->InspectStation(ETSTSSInspectionStation::Lift))) return false;
    TestEqual(TEXT("Pressure becomes next"), State->GetReviewObjectiveText(),
        FString(TEXT("Inspect the pressure systems")));
    if (!TestTrue(TEXT("Inspect reserve out of suggested order"), State->InspectStation(ETSTSSInspectionStation::Reserve))) return false;
    TestEqual(TEXT("Incomplete pressure is still shown"), State->GetReviewObjectiveText(),
        FString(TEXT("Inspect the pressure systems")));
    if (!TestTrue(TEXT("Inspect pressure"), State->InspectStation(ETSTSSInspectionStation::Pressure))) return false;
    TestEqual(TEXT("Signoff now available"), State->GetReviewObjectiveText(),
        FString(TEXT("Complete engineering signoff")));
    const uint8 BeforeMask = State->GetInspectionMask();
    const ETSTSSFirstWakeBeat BeforeBeat = State->GetCurrentBeat();
    State->GetReviewObjectiveText();
    TestEqual(TEXT("Reading objective never edits mask"), State->GetInspectionMask(), BeforeMask);
    TestEqual(TEXT("Reading objective never edits beat"), State->GetCurrentBeat(), BeforeBeat);
    if (!TestTrue(TEXT("Engineering approval"), State->AdvanceTo(ETSTSSFirstWakeBeat::EngineeringChecked))) return false;
    TestEqual(TEXT("Launch next"), State->GetReviewObjectiveText(),
        FString(TEXT("Prepare for the First Wake launch")));
    if (!TestTrue(TEXT("Launch"), State->AdvanceTo(ETSTSSFirstWakeBeat::Launched))) return false;
    TestEqual(TEXT("Flight next"), State->GetReviewObjectiveText(),
        FString(TEXT("Navigate the First Wake flight")));
    TestFalse(TEXT("Cue cannot forge sea contact"), State->IsChapterOneActOne());

    if (!TestTrue(TEXT("Restore observed sea contact"), State->Restore(true, ETSTSSFirstWakeBeat::SeaContact, 0x07))) return false;
    TestEqual(TEXT("Water stability next"), State->GetReviewObjectiveText(),
        FString(TEXT("Stabilize the water landing")));
    if (!TestTrue(TEXT("Restore genuine flotation state"), State->Restore(true, ETSTSSFirstWakeBeat::FlotationConfirmed, 0x07))) return false;
    TestEqual(TEXT("Reserve investigation next"), State->GetReviewObjectiveText(),
        FString(TEXT("Investigate the empty reserves")));
    TestTrue(TEXT("Chapter 1 boundary still derived from state"), State->IsChapterOneActOne());
    if (!TestTrue(TEXT("Restore empty-reserve inspection"), State->Restore(true, ETSTSSFirstWakeBeat::EmptyReserveInspected, 0x07))) return false;
    TestEqual(TEXT("Return objective"), State->GetReviewObjectiveText(), FString(TEXT("Return to berth")));
    if (!TestTrue(TEXT("Restore last review beat"), State->Restore(true, ETSTSSFirstWakeBeat::ReturnedToBerth, 0x07))) return false;
    TestEqual(TEXT("Read-only terminal cue"), State->GetReviewObjectiveText(),
        FString(TEXT("First Wake review sequence complete")));
    State->Reset();
    TestEqual(TEXT("Reset returns objective to flyer"), State->GetReviewObjectiveText(),
        FString(TEXT("Find Ionia's flyer")));
    return true;
}
#endif
