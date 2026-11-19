#include "Misc/AutomationTest.h"
#include "TSTSSMilestoneActor.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSManualMilestoneGuardTest,
    "TSTSS.FirstWake.ManualMilestonesRejectPhysicsEvents",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTSTSSManualMilestoneGuardTest::RunTest(const FString& Parameters)
{
    TestTrue(TEXT("Flyer can be manually inspected"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Ionia can be hired through story interaction"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(ETSTSSFirstWakeBeat::IoniaHired));
    TestTrue(TEXT("Engineering signoff is available after state validation"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestFalse(TEXT("Sea contact requires physics evidence"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(ETSTSSFirstWakeBeat::SeaContact));
    TestFalse(TEXT("Flotation requires sustained physics evidence"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(ETSTSSFirstWakeBeat::FlotationConfirmed));
    TestFalse(TEXT("Unknown enum cannot be manually activated"),
        ATSTSSMilestoneActor::IsManualBeatAllowed(static_cast<ETSTSSFirstWakeBeat>(255)));
    return true;
}
#endif
