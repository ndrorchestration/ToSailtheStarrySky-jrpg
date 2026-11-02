#include "AureateWakePreviewActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"

#if WITH_DEV_AUTOMATION_TESTS
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTSTSSAureateBridgeHabitationReviewTest,
    "TSTSS.Ship.CentralBridgeHabitationReview",
    EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FTSTSSAureateBridgeHabitationReviewTest::RunTest(const FString& Parameters)
{
    // This is a transient preview, not an approved interior or flight mode.
    UWorld* ReviewWorld = UWorld::CreateWorld(EWorldType::Game, false,
        FName(TEXT("TSTSSBridgeHabitationReviewWorld")));
    if (!TestNotNull(TEXT("Transient pivot review world"), ReviewWorld)) return false;
    AAureateWakePreviewActor* Ship = ReviewWorld->SpawnActor<AAureateWakePreviewActor>();
    if (!TestNotNull(TEXT("Bridge pivot actor"), Ship))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }

    USceneComponent* Pivot = nullptr;
    UStaticMeshComponent* Bridge = nullptr;
    UStaticMeshComponent* Quarters = nullptr;
    TArray<USceneComponent*> Components;
    Ship->GetComponents<USceneComponent>(Components);
    for (USceneComponent* Component : Components)
    {
        if (!Component) continue;
        if (Component->GetFName() == FName(TEXT("BridgeHabitationPivot"))) Pivot = Component;
        if (Component->GetFName() == FName(TEXT("ForwardBridge"))) Bridge = Cast<UStaticMeshComponent>(Component);
        if (Component->GetFName() == FName(TEXT("LivingQuartersEnvelope"))) Quarters = Cast<UStaticMeshComponent>(Component);
    }
    if (!TestNotNull(TEXT("Shared habitation pivot"), Pivot) ||
        !TestNotNull(TEXT("Recognizable dome proxy"), Bridge) ||
        !TestNotNull(TEXT("Coupled living quarters envelope"), Quarters))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }

    TestFalse(TEXT("Bridge pivot disabled by default"), Ship->bPreviewCentralBridgeHabitation);
    TestTrue(TEXT("Original forward bridge pose preserved"),
        Bridge->GetRelativeLocation().Equals(FVector(240.f, 0.f, 95.f), .01f));
    TestTrue(TEXT("Legacy pivot origin is unchanged"),
        Pivot->GetRelativeLocation().Equals(FVector::ZeroVector, .01f));
    TestFalse(TEXT("Default living quarters proxy hidden"), Quarters->IsVisible());
    TestEqual(TEXT("Bridge collision disabled"), Bridge->GetCollisionEnabled(), ECollisionEnabled::NoCollision);
    TestEqual(TEXT("Quarters collision disabled"), Quarters->GetCollisionEnabled(), ECollisionEnabled::NoCollision);
    TestTrue(TEXT("Bridge attaches to shared pivot"), Bridge->GetAttachParent() == Pivot);
    TestTrue(TEXT("Living quarters attach to same pivot"), Quarters->GetAttachParent() == Pivot);

    // Values below are review-test inputs, NOT creator-approved form angles.
    Ship->SkyborneHabitationReviewRotation = FRotator::ZeroRotator;
    Ship->SeaborneHabitationReviewRotation = FRotator(0.f, 30.f, 0.f);
    Ship->SubmersibleHabitationReviewRotation = FRotator(0.f, 75.f, 0.f);
    Ship->bPreviewCentralBridgeHabitation = true;
    TestTrue(TEXT("Opt-in preview applies only while idle"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestTrue(TEXT("Coupled center pivot shifts into review position"),
        Pivot->GetRelativeLocation().Equals(FVector(0.f, 0.f, 50.f), .01f));
    TestTrue(TEXT("Bridge moves above central quarters"),
        Bridge->GetRelativeLocation().Equals(FVector(0.f, 0.f, 80.f), .01f));
    TestTrue(TEXT("Quarters visible only when review opted in"), Quarters->IsVisible());

    TestFalse(TEXT("Starbourne (internal Orbiter) is still story gated"),
        Ship->RequestForm(EAureateWakeForm::Orbiter));
    TestTrue(TEXT("Skyborne-to-Seaborne start"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    TestFalse(TEXT("Cannot reparent while transition is moving"),
        Ship->RefreshCentralBridgeHabitationReview());
    Ship->Tick(Ship->TransitionSeconds * .5f);
    TestTrue(TEXT("Coupled habitation pivot moves halfway"),
        FMath::IsNearlyEqual(Pivot->GetRelativeRotation().Yaw, 15.f, .1f));
    TestTrue(TEXT("Bridge and quarters stay on shared moving pivot"),
        Bridge->GetAttachParent() == Pivot && Quarters->GetAttachParent() == Pivot);
    TestTrue(TEXT("Seaborne transition completes"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestTrue(TEXT("Seaborne review angle reached"),
        FMath::IsNearlyEqual(Pivot->GetRelativeRotation().Yaw, 30.f, .1f));
    TestTrue(TEXT("Submersible transition allowed"),
        Ship->RequestForm(EAureateWakeForm::Submersible));
    TestTrue(TEXT("Submersible transition completes"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestTrue(TEXT("Submersible review angle reached"),
        FMath::IsNearlyEqual(Pivot->GetRelativeRotation().Yaw, 75.f, .1f));

    TestTrue(TEXT("Return to Skyborne allowed"), Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestTrue(TEXT("Return to Skyborne completed"), Ship->FinishOrdinaryPreviewTransitionForReview());
    TestTrue(TEXT("Skyborne review angle restored"),
        FMath::IsNearlyZero(Pivot->GetRelativeRotation().Yaw, .1f));
    Ship->bPreviewCentralBridgeHabitation = false;
    TestTrue(TEXT("Opt out restores previous static bridge pose"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestTrue(TEXT("Original bridge position restored"),
        Bridge->GetRelativeLocation().Equals(FVector(240.f,0.f,95.f),.01f));
    TestTrue(TEXT("Central pivot returned to identity position"),
        Pivot->GetRelativeLocation().Equals(FVector::ZeroVector,.01f));
    TestFalse(TEXT("No additional quarters art shown when disabled"), Quarters->IsVisible());
    TestEqual(TEXT("Original four wing components retained"), Ship->GetWingCount(), 4);
    TestEqual(TEXT("Original two foil components retained"), Ship->GetHydrofoilCount(), 2);

    ReviewWorld->DestroyWorld(false);
    return true;
}
#endif
