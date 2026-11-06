#include "Misc/AutomationTest.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSMilestoneActor.h"
#include "TSTSSWaterLandingGate.h"
#include "TSTSSSaveGame.h"
#include "TSTSSReviewContinueManifest.h"
#include "Engine/World.h"
#include "Components/PrimitiveComponent.h"

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

    TestFalse(TEXT("Cannot board before discovering flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestFalse(TEXT("Cannot hire Ionia before discovering flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::IoniaHired));
    TestFalse(TEXT("Chapter 1 unavailable before story begins"), Story->IsChapterOneActOne());
    TestTrue(TEXT("Ender can inspect Ionia hiring flyer"),
        ActivateBeat(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestFalse(TEXT("Flyer interaction cannot be repeated"),
        ActivateBeat(ETSTSSFirstWakeBeat::FlyerDiscovered));
    TestTrue(TEXT("Ionia is hired before boarding"),
        ActivateBeat(ETSTSSFirstWakeBeat::IoniaHired));
    TestTrue(TEXT("Board Aureate Wake in sequence"),
        ActivateBeat(ETSTSSFirstWakeBeat::BoardedAureateWake));
    TestFalse(TEXT("Engineering clearance blocked until every inspection"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Lift station interaction accepted"), Inspect(ETSTSSInspectionStation::Lift));
    TestFalse(TEXT("Duplicate lift evidence cannot advance"), Inspect(ETSTSSInspectionStation::Lift));
    TestTrue(TEXT("Pressure station interaction accepted"), Inspect(ETSTSSInspectionStation::Pressure));
    TestFalse(TEXT("Reserve still missing blocks clearance"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("Reserve station interaction accepted"), Inspect(ETSTSSInspectionStation::Reserve));
    TestTrue(TEXT("Three inspections unlock engineering signoff"),
        ActivateBeat(ETSTSSFirstWakeBeat::EngineeringChecked));
    TestTrue(TEXT("First flight genuinely launches"), ActivateBeat(ETSTSSFirstWakeBeat::Launched));
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

    // No Lyra recruitment is synthesized here. Existing recovery milestones
    // take place only after the physical boundary.
    TestTrue(TEXT("Inspect empty reserve after Splashdown"),
        ActivateBeat(ETSTSSFirstWakeBeat::EmptyReserveInspected));
    TestTrue(TEXT("Return to berth is post-Splashdown"),
        ActivateBeat(ETSTSSFirstWakeBeat::ReturnedToBerth));
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

#if WITH_EDITOR
    // Native sidecar provenance and no-flight-restore contract. This tests
    // the actual Unreal SaveGame UObject class without writing a user slot.
    UTSTSSSaveGame* ContinuePrimary =
        NewObject<UTSTSSSaveGame>(GetTransientPackage());
    ContinuePrimary->bFirstWakeStarted = true;
    ContinuePrimary->FirstWakeBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    UTSTSSReviewContinueManifest* ContinueManifest =
        NewObject<UTSTSSReviewContinueManifest>(GetTransientPackage());
    ContinueManifest->PrimarySlot = TEXT("tstss_prelude_pie_quick");
    ContinueManifest->ProjectRoot = TEXT("C:/TSTSS_ReviewSandbox/unreal/");
    ContinueManifest->ReviewMapPackage =
        TEXT("/Game/TSTSS/Review/FirstWake_LaunchWaterGreybox_V1");
    ContinueManifest->PrimaryBlake3_160 =
        TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
    ContinueManifest->bSavedStoryStarted = true;
    ContinueManifest->SavedBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    ContinueManifest->SavedPawnLocation = FVector(-1300.f, 0.f, 90.f);
    const auto Bound = [ContinueManifest, ContinuePrimary](
        const FString& Project, const FString& Map,
        const FString& Digest) -> bool
    {
        return ContinueManifest->IsBoundFor(ContinuePrimary,
            TEXT("tstss_prelude_pie_quick"), Project, Map, Digest);
    };
    const FString GoodProject = ContinueManifest->ProjectRoot;
    const FString GoodMap = ContinueManifest->ReviewMapPackage;
    const FString GoodDigest = ContinueManifest->PrimaryBlake3_160;
    TestTrue(TEXT("Only manifest bound to exact v2 review save can Continue"),
        Bound(GoodProject, GoodMap, GoodDigest));
    TestFalse(TEXT("Foreign source project cannot Continue"),
        Bound(TEXT("C:/OtherGame/"), GoodMap, GoodDigest));
    TestFalse(TEXT("Foreign review map cannot Continue"),
        Bound(GoodProject, TEXT("/Game/TSTSS/OtherMap"), GoodDigest));
    TestFalse(TEXT("Mutated primary bytes cannot Continue"),
        Bound(GoodProject, GoodMap,
            TEXT("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")));
    ContinueManifest->ReviewVersion = 99;
    TestFalse(TEXT("Unknown future sidecar rejected"),
        Bound(GoodProject, GoodMap, GoodDigest));
    ContinueManifest->ReviewVersion =
        UTSTSSReviewContinueManifest::CurrentReviewVersion;
    ContinueManifest->SavedPawnLocation = FVector(100001.f, 0.f, 90.f);
    TestFalse(TEXT("Out-of-bounds pawn location rejected"),
        Bound(GoodProject, GoodMap, GoodDigest));
    ContinueManifest->SavedPawnLocation = FVector(-1300.f, 0.f, 90.f);
    ContinuePrimary->FirstWakeBeat = ETSTSSFirstWakeBeat::Launched;
    ContinuePrimary->InspectionMask = 0x07;
    ContinueManifest->SavedBeat = ETSTSSFirstWakeBeat::Launched;
    ContinueManifest->SavedInspectionMask = 0x07;
    TestFalse(TEXT("Uncaptured ship flight cannot be restored"),
        Bound(GoodProject, GoodMap, GoodDigest));
    ContinuePrimary->FirstWakeBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    ContinuePrimary->InspectionMask = 0;
    ContinueManifest->SavedBeat = ETSTSSFirstWakeBeat::FlyerDiscovered;
    ContinueManifest->SavedInspectionMask = 0;
    TestTrue(TEXT("Prelaunch Continue binding remains allowed"),
        Bound(GoodProject, GoodMap, GoodDigest));

    // Native PIE-world contract for both review namespaces. Consumed
    // splashdown markers must release the camera ray and pawn, but rejected
    // milestones and unrelated production actors must keep their collision.
    UWorld* ReviewWorld = UWorld::CreateWorld(
        EWorldType::PIE, false, FName(TEXT("TSTSSConsumedSplashdownReviewTest")));
    if (!TestNotNull(TEXT("Transient PIE-world available"), ReviewWorld))
    {
        World->DestroyWorld(false);
        return false;
    }
    UTSTSSFirstWakeState* LaunchStory =
        NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    TestTrue(TEXT("Bounded test story can restore prelaunch engineering signoff"),
        LaunchStory->Restore(true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x07));
    ATSTSSMilestoneActor* LaunchMarker =
        ReviewWorld->SpawnActor<ATSTSSMilestoneActor>();
    if (TestNotNull(TEXT("Real splashdown review milestone spawned"), LaunchMarker))
    {
        LaunchMarker->SetActorLabel(
            TEXT("TSTSS_SPLASHDOWN_GREYBOX_LaunchMarker"));
        LaunchMarker->Milestone = ETSTSSFirstWakeBeat::Launched;
        UPrimitiveComponent* ReviewMesh =
            Cast<UPrimitiveComponent>(LaunchMarker->GetRootComponent());
        if (TestNotNull(TEXT("Review collision component exists"), ReviewMesh))
        {
            TestEqual(TEXT("Launch marker visibility initially blocks ray"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
            TestTrue(TEXT("Launch accepted by real native actor"),
                LaunchMarker->TryActivate(LaunchStory));
            TestEqual(TEXT("Accepted launch marker releases visibility ray"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
            TestEqual(TEXT("Accepted launch marker releases pawn movement"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Pawn), ECR_Ignore);
            TestFalse(TEXT("Consumed launch marker cannot advance twice"),
                LaunchMarker->TryActivate(LaunchStory));
            TestTrue(TEXT("Quickload rehearsal restores prelaunch signoff"),
                LaunchStory->Restore(
                    true, ETSTSSFirstWakeBeat::EngineeringChecked, 0x07));
            LaunchMarker->ReconcileReviewCollisionAfterRestore(LaunchStory);
            TestEqual(TEXT("Quickload reactivates not-yet-launched visibility"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
            TestEqual(TEXT("Quickload reactivates not-yet-launched pawn blocking"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Pawn), ECR_Block);
            TestTrue(TEXT("Reactivated launch requires and accepts a fresh E"),
                LaunchMarker->TryActivate(LaunchStory));
            TestEqual(TEXT("Fresh accepted E again releases launch marker"),
                ReviewMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
        }
    }

    ATSTSSMilestoneActor* RejectedMarker =
        ReviewWorld->SpawnActor<ATSTSSMilestoneActor>();
    UTSTSSFirstWakeState* Unstarted =
        NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    if (TestNotNull(TEXT("Rejected marker exists"), RejectedMarker))
    {
        RejectedMarker->SetActorLabel(
            TEXT("TSTSS_SPLASHDOWN_GREYBOX_LaunchMarker"));
        RejectedMarker->Milestone = ETSTSSFirstWakeBeat::Launched;
        UPrimitiveComponent* RejectedMesh =
            Cast<UPrimitiveComponent>(RejectedMarker->GetRootComponent());
        TestFalse(TEXT("Out-of-order launch denied"), RejectedMarker->TryActivate(Unstarted));
        if (TestNotNull(TEXT("Rejected marker mesh exists"), RejectedMesh))
        {
            TestEqual(TEXT("Rejected launch marker must retain visibility block"),
                RejectedMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
        }
    }

    ATSTSSMilestoneActor* NonReview =
        ReviewWorld->SpawnActor<ATSTSSMilestoneActor>();
    UTSTSSFirstWakeState* NonReviewStory =
        NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    if (TestNotNull(TEXT("Unrelated actor exists"), NonReview))
    {
        NonReview->SetActorLabel(TEXT("TSTSS_PRODUCTION_ShipInteraction"));
        NonReview->Milestone = ETSTSSFirstWakeBeat::FlyerDiscovered;
        UPrimitiveComponent* NonReviewMesh =
            Cast<UPrimitiveComponent>(NonReview->GetRootComponent());
        TestTrue(TEXT("Non-review milestone still follows story"),
            NonReview->TryActivate(NonReviewStory));
        if (TestNotNull(TEXT("Unrelated actor mesh exists"), NonReviewMesh))
        {
            NonReview->ReconcileReviewCollisionAfterRestore(NonReviewStory);
            TestEqual(TEXT("Production-like actor keeps visibility blocking"),
                NonReviewMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
        }
    }

    UTSTSSFirstWakeState* SavedIoniaStory =
        NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    TestTrue(TEXT("Valid saved Ionia beat is restorable"),
        SavedIoniaStory->Restore(true, ETSTSSFirstWakeBeat::IoniaHired, 0));
    ATSTSSMilestoneActor* AlreadyCompletedFlyer =
        ReviewWorld->SpawnActor<ATSTSSMilestoneActor>();
    if (TestNotNull(TEXT("Completed flyer review actor exists"), AlreadyCompletedFlyer))
    {
        AlreadyCompletedFlyer->SetActorLabel(
            TEXT("TSTSS_PRELUDE_REVIEW_FlyerDiscovery"));
        AlreadyCompletedFlyer->Milestone = ETSTSSFirstWakeBeat::FlyerDiscovered;
        UPrimitiveComponent* CompletedMesh =
            Cast<UPrimitiveComponent>(AlreadyCompletedFlyer->GetRootComponent());
        AlreadyCompletedFlyer->ReconcileReviewCollisionAfterRestore(SavedIoniaStory);
        if (TestNotNull(TEXT("Completed flyer mesh exists"), CompletedMesh))
        {
            TestEqual(TEXT("Saved-complete flyer remains transparent to camera"),
                CompletedMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
        }
    }

    UTSTSSFirstWakeState* PartialInspectionStory =
        NewObject<UTSTSSFirstWakeState>(GetTransientPackage());
    TestTrue(TEXT("Valid pre-inspection save restores"), PartialInspectionStory->Restore(
        true, ETSTSSFirstWakeBeat::BoardedAureateWake, 0));
    ATSTSSMilestoneActor* LiftReview =
        ReviewWorld->SpawnActor<ATSTSSMilestoneActor>();
    if (TestNotNull(TEXT("Native review inspection marker exists"), LiftReview))
    {
        LiftReview->SetActorLabel(TEXT("TSTSS_PRELUDE_REVIEW_LiftStation"));
        LiftReview->bIsInspectionStation = true;
        LiftReview->InspectionStation = ETSTSSInspectionStation::Lift;
        UPrimitiveComponent* LiftMesh =
            Cast<UPrimitiveComponent>(LiftReview->GetRootComponent());
        LiftReview->ReconcileReviewCollisionAfterRestore(PartialInspectionStory);
        if (TestNotNull(TEXT("Lift review mesh exists"), LiftMesh))
        {
            TestEqual(TEXT("Uninspected lift remains interactable after restore"),
                LiftMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Block);
            TestTrue(TEXT("Save with only Lift inspection can restore"),
                PartialInspectionStory->Restore(
                    true, ETSTSSFirstWakeBeat::BoardedAureateWake, 0x01));
            LiftReview->ReconcileReviewCollisionAfterRestore(PartialInspectionStory);
            TestEqual(TEXT("Already inspected Lift stops blocking on load"),
                LiftMesh->GetCollisionResponseToChannel(ECC_Visibility), ECR_Ignore);
        }
    }
    ReviewWorld->DestroyWorld(false);
#endif

    // No player save slot is written; do not alter any gameplay session.
    World->DestroyWorld(false);
    return true;
}
#endif
