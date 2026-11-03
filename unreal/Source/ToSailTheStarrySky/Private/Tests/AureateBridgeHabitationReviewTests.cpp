#include "AureateWakePreviewActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/World.h"
#include "Misc/AutomationTest.h"
#include <limits>

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
    USceneComponent* HelmAnchor = nullptr;
    USceneComponent* QuartersAnchor = nullptr;
    USceneComponent* EngineeringAnchor = nullptr;
    USceneComponent* BoardingAnchor = nullptr;
    TArray<USceneComponent*> Components;
    Ship->GetComponents<USceneComponent>(Components);
    for (USceneComponent* Component : Components)
    {
        if (!Component) continue;
        if (Component->GetFName() == FName(TEXT("BridgeHabitationPivot"))) Pivot = Component;
        if (Component->GetFName() == FName(TEXT("ForwardBridge"))) Bridge = Cast<UStaticMeshComponent>(Component);
        if (Component->GetFName() == FName(TEXT("LivingQuartersEnvelope"))) Quarters = Cast<UStaticMeshComponent>(Component);
        if (Component->GetFName() == FName(TEXT("BridgeHelmReviewAnchor"))) HelmAnchor = Component;
        if (Component->GetFName() == FName(TEXT("QuartersDeckReviewAnchor"))) QuartersAnchor = Component;
        if (Component->GetFName() == FName(TEXT("FixedEngineeringReviewAnchor"))) EngineeringAnchor = Component;
        if (Component->GetFName() == FName(TEXT("FixedBoardingReviewAnchor"))) BoardingAnchor = Component;
    }
    if (!TestNotNull(TEXT("Shared habitation pivot"), Pivot) ||
        !TestNotNull(TEXT("Recognizable dome proxy"), Bridge) ||
        !TestNotNull(TEXT("Coupled living quarters envelope"), Quarters))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }

    if (!TestNotNull(TEXT("Bridge/helm review anchor"), HelmAnchor) ||
        !TestNotNull(TEXT("Quarters/deck review anchor"), QuartersAnchor) ||
        !TestNotNull(TEXT("Engineering hull review anchor"), EngineeringAnchor) ||
        !TestNotNull(TEXT("Boarding hull review anchor"), BoardingAnchor))
    {
        ReviewWorld->DestroyWorld(false);
        return false;
    }
    TestTrue(TEXT("Helm and quarters anchors share the rotating frame"),
        HelmAnchor->GetAttachParent() == Pivot && QuartersAnchor->GetAttachParent() == Pivot);
    TestTrue(TEXT("Engineering and boarding anchors stay on fixed hull"),
        EngineeringAnchor->GetAttachParent() == Ship->GetRootComponent() &&
        BoardingAnchor->GetAttachParent() == Ship->GetRootComponent());
    TestTrue(TEXT("Default helm anchor matches legacy bridge"),
        HelmAnchor->GetRelativeLocation().Equals(FVector(240.f, 0.f, 95.f), .01f));
    TestTrue(TEXT("Quarters anchor follows deck local offset"),
        QuartersAnchor->GetRelativeLocation().Equals(FVector(0.f, 0.f, -25.f), .01f));

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
    TestTrue(TEXT("Opt-in helm anchor follows dome center"),
        HelmAnchor->GetRelativeLocation().Equals(Bridge->GetRelativeLocation(), .01f));
    TestTrue(TEXT("Fixed engineering station is not carried by rotating pivot"),
        EngineeringAnchor->GetAttachParent() == Ship->GetRootComponent());

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
    // A direct Inspector/Blueprint bool edit during movement must NOT strand
    // a rotated bridge after completion, and an opt-in pivot must not defeat
    // Orbiter safety even if the older cube-art preview toggle is true.
    Ship->bAllowOrbiterPreview = true;
    Ship->bPreviewCentralBridgeHabitation = true;
    TestTrue(TEXT("Review pivot can re-enable while idle"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestFalse(TEXT("Central habitation cannot use unvalidated Orbiter path"),
        Ship->RequestForm(EAureateWakeForm::Orbiter));
    TestTrue(TEXT("Ordinary movement still begins"), Ship->RequestForm(EAureateWakeForm::Seaborne));
    Ship->Tick(Ship->TransitionSeconds * .5f);
    const float BeforeDeferredToggleYaw = Pivot->GetRelativeRotation().Yaw;
    Ship->bPreviewCentralBridgeHabitation = false;
    TestFalse(TEXT("Live preview refresh cannot mutate active motion"),
        Ship->RefreshCentralBridgeHabitationReview());
    Ship->Tick(Ship->TransitionSeconds * .25f);
    TestTrue(TEXT("Latched pivot motion finishes without an abrupt midflight reset"),
        Pivot->GetRelativeRotation().Yaw > BeforeDeferredToggleYaw);
    TestTrue(TEXT("Midflight opt-out completes original ordinary route"),
        Ship->FinishOrdinaryPreviewTransitionForReview());
    TestTrue(TEXT("Deferred opt-out restores original bridge translation"),
        Bridge->GetRelativeLocation().Equals(FVector(240.f,0.f,95.f),.01f));
    TestTrue(TEXT("Deferred opt-out resets the pivot position"),
        Pivot->GetRelativeLocation().Equals(FVector::ZeroVector,.01f));
    TestTrue(TEXT("Deferred opt-out resets the pivot rotation"),
        Pivot->GetRelativeRotation().IsNearlyZero(.01f));
    TestFalse(TEXT("Deferred opt-out hides quarters"), Quarters->IsVisible());

    // Exercise all six directed ordinary transitions with the coupled
    // habitation opt-in. This is a preview transform test, NOT physics/CCD.
    Ship->bAllowOrbiterPreview = false;
    Ship->bPreviewCentralBridgeHabitation = true;
    TestTrue(TEXT("Six-route habitation review enabled while idle"),
        Ship->RefreshCentralBridgeHabitationReview());
    const EAureateWakeForm OrdinaryForms[] = {
        EAureateWakeForm::Skyborne,
        EAureateWakeForm::Seaborne,
        EAureateWakeForm::Submersible
    };
    const auto PreviewYaw = [](EAureateWakeForm Form) -> float
    {
        switch (Form)
        {
        case EAureateWakeForm::Seaborne: return 30.f;
        case EAureateWakeForm::Submersible: return 75.f;
        default: return 0.f;
        }
    };
    int32 DirectedRoutes = 0;
    for (const EAureateWakeForm Start : OrdinaryForms)
    {
        if (Ship->GetCurrentForm() != Start)
        {
            TestTrue(TEXT("Can navigate to an ordinary start form"),
                Ship->RequestForm(Start));
            TestTrue(TEXT("Ordinary start form reached"),
                Ship->FinishOrdinaryPreviewTransitionForReview());
        }
        for (const EAureateWakeForm Target : OrdinaryForms)
        {
            if (Start == Target) continue;
            if (Ship->GetCurrentForm() != Start)
            {
                TestTrue(TEXT("Can return to the route start form"),
                    Ship->RequestForm(Start));
                TestTrue(TEXT("Route start reached"),
                    Ship->FinishOrdinaryPreviewTransitionForReview());
            }
            TestFalse(TEXT("Starbourne stays gated during six-route review"),
                Ship->RequestForm(EAureateWakeForm::Orbiter));
            TestTrue(TEXT("Ordinary coupled-pivot route starts"), Ship->RequestForm(Target));
            Ship->Tick(Ship->TransitionSeconds * .5f);
            TestTrue(TEXT("Pivot follows review-only midpoint yaw"),
                FMath::IsNearlyEqual(Pivot->GetRelativeRotation().Yaw,
                    .5f * (PreviewYaw(Start) + PreviewYaw(Target)), 1.0f));
            TestTrue(TEXT("Dome and quarters remain parented during each route"),
                Bridge->GetAttachParent() == Pivot && Quarters->GetAttachParent() == Pivot);
            TestTrue(TEXT("Quarters remain visible during pivot review"),
                Quarters->IsVisible());
            TestTrue(TEXT("Ordinary coupled-pivot route finishes"),
                Ship->FinishOrdinaryPreviewTransitionForReview());
            TestEqual(TEXT("Directed form completed"), Ship->GetCurrentForm(), Target);
            TestTrue(TEXT("Pivot reaches review-only target yaw"),
                FMath::IsNearlyEqual(Pivot->GetRelativeRotation().Yaw,
                    PreviewYaw(Target), 1.0f));
            ++DirectedRoutes;
        }
    }
    TestEqual(TEXT("All six directed coupled-pivot routes covered"), DirectedRoutes, 6);
    Ship->bPreviewCentralBridgeHabitation = false;
    TestTrue(TEXT("Six-route preview can restore legacy layout"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestTrue(TEXT("Final legacy bridge pose restored"),
        Bridge->GetRelativeLocation().Equals(FVector(240.f,0.f,95.f),.01f));
    TestFalse(TEXT("Final quarters stand-in hidden"), Quarters->IsVisible());
    TestTrue(TEXT("Opt-out restores helm anchor with original bridge"),
        HelmAnchor->GetRelativeLocation().Equals(FVector(240.f, 0.f, 95.f), .01f));
    TestTrue(TEXT("Opt-out preserves two independent fixed hull anchors"),
        EngineeringAnchor->GetAttachParent() == Ship->GetRootComponent() &&
        BoardingAnchor->GetAttachParent() == Ship->GetRootComponent());

    // A malformed inspector or Blueprint angle must not inject NaN/Inf
    // into either child's transform or consume the ship transition state.
    // These non-finite values are deliberately assigned to the existing
    // FRotator fields, avoiding constructor-time normalization.
    Ship->bPreviewCentralBridgeHabitation = true;
    TestTrue(TEXT("Finite bridge review can re-enable before invalid-input tests"),
        Ship->RefreshCentralBridgeHabitationReview());
    const FQuat BeforeBadPose = Pivot->GetRelativeRotation().Quaternion();
    const FVector BeforeBadLocation = Pivot->GetRelativeLocation();
    const EAureateWakeForm BeforeBadForm = Ship->GetCurrentForm();
    Ship->SkyborneHabitationReviewRotation.Yaw =
        std::numeric_limits<float>::quiet_NaN();
    TestFalse(TEXT("NaN destination angle rejects a form request atomically"),
        Ship->RequestForm(EAureateWakeForm::Skyborne));
    TestFalse(TEXT("NaN destination cannot start bridge motion"), Ship->IsTransitioning());
    TestEqual(TEXT("NaN destination preserves form"), Ship->GetCurrentForm(), BeforeBadForm);
    TestTrue(TEXT("NaN destination leaves pivot rotation unchanged"),
        Pivot->GetRelativeRotation().Quaternion().Equals(BeforeBadPose, .001f));
    TestTrue(TEXT("NaN destination leaves pivot location unchanged"),
        Pivot->GetRelativeLocation().Equals(BeforeBadLocation, .001f));
    Ship->SkyborneHabitationReviewRotation.Yaw = 0.f;

    // Current-form nonfinite input also rejects refresh before relocating
    // the dome and quarters; opt-out still recovers the static preview.
    Ship->SeaborneHabitationReviewRotation.Yaw =
        std::numeric_limits<float>::infinity();
    TestFalse(TEXT("Infinity in active review angle blocks refresh"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestFalse(TEXT("Infinity in active review angle blocks movement"),
        Ship->RequestForm(EAureateWakeForm::Submersible));
    TestTrue(TEXT("Invalid active review angle leaves pivot intact"),
        Pivot->GetRelativeRotation().Quaternion().Equals(BeforeBadPose, .001f) &&
        Pivot->GetRelativeLocation().Equals(BeforeBadLocation, .001f));
    Ship->bPreviewCentralBridgeHabitation = false;
    TestTrue(TEXT("Opt out recovers even with an invalid stored editor angle"),
        Ship->RefreshCentralBridgeHabitationReview());
    TestFalse(TEXT("Opt out hides review quarters"), Quarters->IsVisible());
    Ship->SeaborneHabitationReviewRotation.Yaw = 30.f;

    TestEqual(TEXT("Original four wing components retained"), Ship->GetWingCount(), 4);
    TestEqual(TEXT("Original two foil components retained"), Ship->GetHydrofoilCount(), 2);

    ReviewWorld->DestroyWorld(false);
    return true;
}
#endif
