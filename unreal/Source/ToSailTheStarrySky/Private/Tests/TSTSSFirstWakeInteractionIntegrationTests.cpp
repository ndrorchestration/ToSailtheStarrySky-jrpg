#include "Misc/AutomationTest.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSWaterLandingGate.h"
#include "TSTSSSaveGame.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"

#if WITH_DEV_AUTOMATION_TESTS

// Bounded integration proof: native milestone actors -> story state -> physical
// landing gate -> Chapter 1 boundary -> recovery interactions -> save payload.
// No level traversal, camera controls, buoyancy, renderer or art is exercised.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
    FTSTSSFirstWakeInteractionSplashdownTest,
    "TSTSS.FirstWake.InteractionToSplashdown",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSFirstWakeInteractionSplashdownTest::RunTest(const FString& Parameters)
{
    UWorld* World = UWorld::CreateWorld(
        EWorldType::Game, false, FName(TEXT("TSTSSFirstWakeIntegrationTransient")));
    if (!TestNotNull(TEXT("Transient First Wake test world exists"), World))
    {
        return false;
    }

    UTSTSSFirstWakeState* Story = NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    UTSTSSWaterLandingGate* WaterGate = NewObject<UTSTSSWaterLandingGate>(GetTransientPackage());
    ATSTSSMilestoneActor* Trigger = World->SpawnActor<ATSTSSMilestoneActor>();
    if (!TestNotNull(TEXT("Real milestone actor spawned"), Trigger) ||
        !TestNotNull(TEXT("Story state exists"), Story) ||
        !TestNotNull(TEXT("Water gate exists"), WaterGate))
    {
        World->DestroyWorld(false);
        return false;
    }

    UStaticMeshComponent* MarkerMesh = Trigger->FindComponentByClass<UStaticMeshComponent>();
    if (!TestNotNull(TEXT("Interaction marker mesh exists"), MarkerMesh))
    {
        World->DestroyWorld(false);
        return false;
    }
    TestEqual(TEXT("Marker is query-only; it cannot physically obstruct the route"),
        MarkerMesh->GetCollisionEnabled(), ECollisionEnabled::QueryOnly);
    TestEqual(TEXT("Pawn can pass a completed marker"),
        MarkerMesh->GetCollisionResponseToChannel(ECC_Pawn), ECR_Ignore);
    TestEqual(TEXT("E visibility ray still hits the marker"),
        MarkerMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);

    const auto ActivateBeat = [Trigger, Story](ETSTSSFirstWakeBeat Beat) -> bool
    {
        Trigger->bIsInspectionStation = false;
        Trigger->Milestone = Beat;
        return Trigger->TryActivate(Story);
    };
    const auto Inspect = [Trigger, Story](ETSTSSInspectionStation Station) -> bool
    {
        Trigger->bIsInspectionStation = true;
        Trigger->InspectionStation = Station;
        return Trigger->TryActivate(Story);
    };

    TestEqual(TEXT("Opening objective prompts Ender toward flyer"), Story->GetReviewObjectiveText(),
        FString(TEXT("Find Ionia's flyer")));
    TestFalse(TEXT("Cannot board before discovering flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestFalse(TEXT("Cannot hire Ionia before discovering flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::IoniaHired));
    TestFalse(TEXT("Chapter 1 unavailable before story begins"), Story->IsChapterOneActOne());
    TestTrue(TEXT("Ender can inspect Ionia hiring flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestEqual(TEXT("Flyer changes objective to Captain Ionia"), Story->GetReviewObjectiveText(),
        FString(TEXT("Speak with Captain Ionia")));
    TestFalse(TEXT("Flyer interaction cannot be repeated"),
        ActivateBeat(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestEqual(TEXT("Rejected flyer keeps Ionia objective"), Story->GetReviewObjectiveText(),
        FString(TEXT("Speak with Captain Ionia")));
    TestTrue(TEXT("Ionia is hired before boarding"),
        ActivateBeat(ETSTSSFirstWakeBeat::IoniaHired));
    TestEqual(TEXT("Ionia hiring changes objective to ship boarding"), Story->GetReviewObjectiveText(),
        FString(TEXT("Board the Aureate Wake")));
    TestTrue(TEXT("Board Aureate Wake in sequence"),
        ActivateBeat(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestEqual(TEXT("Boarding prompts lift inspection"), Story->GetReviewObjectiveText(),
        FString(TEXT("Inspect the levitation lift")));
    TestFalse(TEXT("Engineering clearance blocked until every inspection"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Lift station interaction accepted"), Inspect(ETSTSSInspectionStation::Lift));
    TestEqual(TEXT("Lift check prompts pressure inspection"), Story->GetReviewObjectiveText(),
        FString(TEXT("Inspect the pressure systems")));
    TestFalse(TEXT("Duplicate lift evidence cannot advance"), Inspect(ETSTSSInspectionStation::Lift));
    TestEqual(TEXT("Duplicate lift preserves pressure objective"), Story->GetReviewObjectiveText(),
        FString(TEXT("Inspect the pressure systems")));
    TestTrue(TEXT("Pressure station interaction accepted"), Inspect(ETSTSSInspectionStation::Pressure));
    TestEqual(TEXT("Pressure check prompts reserve inspection"), Story->GetReviewObjectiveText(),
        FString(TEXT("Inspect the reserve systems")));
    TestFalse(TEXT("Reserve still missing blocks clearance"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Reserve station interaction accepted"), Inspect(ETSTSSInspectionStation::Reserve));
    TestEqual(TEXT("Three inspections prompt engineering signoff"), Story->GetReviewObjectiveText(),
        FString(TEXT("Complete engineering signoff")));
    TestTrue(TEXT("Three inspections unlock engineering signoff"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestEqual(TEXT("Engineering signoff prompts launch"), Story->GetReviewObjectiveText(),
        FString(TEXT("Prepare for the First Wake launch")));
    TestTrue(TEXT("First flight genuinely launches"), ActivateBeat(ETSTSSFirstWakeBeat::Launched));
    TestEqual(TEXT("Launch objective remains in Prelude flight"), Story->GetReviewObjectiveText(),
        FString(TEXT("Navigate the First Wake flight")));
    TestFalse(TEXT("No chapter transition on launch"), Story->IsChapterOneActOne());

    // The interactive actor must never forge water contact or flotation.
    TestFalse(TEXT("Generic interaction cannot manufacture sea contact"),
        ActivateBeat(ETSTSSFirstWakeBeat::SeaContact));
    TestFalse(TEXT("Generic interaction cannot manufacture flotation"),
        ActivateBeat(ETSTSSFirstWakeBeat::FlotationConfirmed));
    TestEqual(TEXT("Still launched after forbidden triggers"), Story->GetCurrentBeat(),
        ETSTSSFirstWakeBeat::Launched);
    TestFalse(TEXT("No collision cannot create sea contact"),
        WaterGate->Observe(0.1f, false, 0.f, Story));
    TestFalse(TEXT("Impact contact alone does not certify float"),
        WaterGate->Observe(0.1f, true, 180.f, Story));
    TestEqual(TEXT("Physical impact records contact"), Story->GetCurrentBeat(),
        ETSTSSFirstWakeBeat::SeaContact);
    TestEqual(TEXT("Sea contact prompts landing stabilization"), Story->GetReviewObjectiveText(),
        FString(TEXT("Stabilize the water landing")));
    TestFalse(TEXT("SeaContact remains Prelude"), Story->IsChapterOneActOne());

    // 1 second of calm then discontinuity: not enough to enter Chapter 1.
    for (int32 Step = 0; Step < 10; ++Step)
    {
        TestFalse(TEXT("Short stable contact is not flotation"),
            WaterGate->Observe(0.1f, true, 5.f, Story));
    }
    TestFalse(TEXT("Contact gap invalidates transient flotation timer"),
        WaterGate->Observe(0.1f, false, 0.f, Story));
    TestEqual(TEXT("Unstable water contact still Prelude"), Story->GetCurrentBeat(),
        ETSTSSFirstWakeBeat::SeaContact);
    TestFalse(TEXT("Unstable water contact still not Chapter 1"), Story->IsChapterOneActOne());

    bool bFloating = false;
    for (int32 Step = 0; Step < 21; ++Step)
    {
        bFloating |= WaterGate->Observe(0.1f, true, 5.f, Story);
    }
    TestTrue(TEXT("Sustained physical contact proves float"), bFloating);
    TestEqual(TEXT("True Splashdown boundary"), Story->GetCurrentBeat(),
        ETSTSSFirstWakeBeat::FlotationConfirmed);
    TestTrue(TEXT("Chapter 1 Act 1 begins ONLY at sustained flotation"),
        Story->IsChapterOneActOne());

    TestEqual(TEXT("Splashdown objective prompts empty reserve investigation"), Story->GetReviewObjectiveText(),
        FString(TEXT("Investigate the empty reserves")));
    // No Lyra recruitment is synthesized here. Existing recovery milestones
    // take place only after the physical boundary.
    TestTrue(TEXT("Inspect empty reserve after Splashdown"),
        ActivateBeat(ETSTSSFirstWakeBeat::EmptyReserveInspected));
    TestEqual(TEXT("Reserve inspection prompts berth recovery"), Story->GetReviewObjectiveText(),
        FString(TEXT("Return to berth")));
    TestTrue(TEXT("Return to berth is post-Splashdown"),
        ActivateBeat(ETSTSSFirstWakeBeat::ReturnedToBerth));
    TestEqual(TEXT("Recovered story has final review objective"), Story->GetReviewObjectiveText(),
        FString(TEXT("First Wake review sequence complete")));
    TestFalse(TEXT("Cannot advance beyond final recovery beat"),
        ActivateBeat(ETSTSSFirstWakeBeat::ReturnedToBerth));
    TestTrue(TEXT("Chapter 1 persists through recovery"), Story->IsChapterOneActOne());

    UTSTSSSaveGame* Snapshot = NewObject<UTSTSSSaveGame>(GetTransientPackage());
    Snapshot->bFirstWakeStarted = Story->HasStarted();
    Snapshot->FirstWakeBeat = Story->GetCurrentBeat();
    Snapshot->InspectionMask = Story->GetInspectionMask();
    TestTrue(TEXT("Resulting recovery state forms a valid v2 save payload"),
        Snapshot->IsStructurallyValid());

    UTSTSSFirstWakeState* Restored = NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    TestTrue(TEXT("Restore simulated save payload in separate state object"),
        Restored->Restore(Snapshot->bFirstWakeStarted,
            Snapshot->FirstWakeBeat, Snapshot->InspectionMask));
    TestTrue(TEXT("Chapter boundary remains after v2 state restoration"),
        Restored->IsChapterOneActOne());
    TestEqual(TEXT("Restored beat retains recovery milestone"),
        Restored->GetCurrentBeat(), ETSTSSFirstWakeBeat::ReturnedToBerth);
    Restored->Reset();
    TestFalse(TEXT("New game reset returns to Prelude"), Restored->IsChapterOneActOne());

    TestEqual(TEXT("Reset restores first objective"), Restored->GetReviewObjectiveText(),
        FString(TEXT("Find Ionia's flyer")));
    // No player save slot is written; do not alter any gameplay session.
    World->DestroyWorld(false);
    return true;
}
#endif
