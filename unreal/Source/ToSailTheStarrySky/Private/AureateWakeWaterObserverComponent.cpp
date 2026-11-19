#include "AureateWakeWaterObserverComponent.h"
#include "AureateWakePreviewActor.h"
#include "Components/PrimitiveComponent.h"

UAureateWakeWaterObserverComponent::UAureateWakeWaterObserverComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
    PrimaryComponentTick.TickInterval = 0.05f;
}

void UAureateWakeWaterObserverComponent::BeginPlay()
{
    Super::BeginPlay();
    LandingGate = NewObject<UTSTSSWaterLandingGate>(this);
}

void UAureateWakeWaterObserverComponent::TickComponent(float DeltaTime,
    ELevelTick TickType, FActorComponentTickFunction* Function)
{
    Super::TickComponent(DeltaTime, TickType, Function);
    if (!IsValid(PhysicalHull) || !IsValid(WaterCollision) ||
        !IsValid(Story) || !IsValid(LandingGate) ||
        !PhysicalHull->GetGenerateOverlapEvents() || !WaterCollision->GetGenerateOverlapEvents())
    {
        if (IsValid(LandingGate)) LandingGate->Reset();
        return; // Unwired components must fail closed and discard stale samples.
    }

    if (!Story->HasStarted())
    {
        LandingGate->Reset();
        return;
    }
    const ETSTSSFirstWakeBeat Beat = Story->GetCurrentBeat();
    if (Beat != ETSTSSFirstWakeBeat::Launched && Beat != ETSTSSFirstWakeBeat::SeaContact)
    {
        LandingGate->Reset();
        return; // Chapter gate: never infer story milestones from geometry.
    }

    const bool bTouchingWater = PhysicalHull->IsOverlappingComponent(WaterCollision);
    // A simulating body can move independently of its owning actor or root.
    // Use the actual rigid-body velocity where possible; otherwise read the
    // kinematic component velocity. Scene wiring still requires native proof.
    const float VerticalSpeed = (PhysicalHull->IsSimulatingPhysics()
        ? PhysicalHull->GetPhysicsLinearVelocity()
        : PhysicalHull->GetComponentVelocity()).Z;
    // Validate the sample with the existing story gate FIRST. A rejected or
    // malformed sample must not trigger a visual landing either.
    if (!FMath::IsFinite(DeltaTime) || DeltaTime <= 0.f ||
        DeltaTime > 0.25f || !FMath::IsFinite(VerticalSpeed))
    {
        LandingGate->Reset();
        return;
    }
    LandingGate->Observe(DeltaTime, bTouchingWater, VerticalSpeed, Story);
    // Request the visual landing only after the story gate has accepted
    // contact. Do not infer acceptance merely from a collider overlap.
    const ETSTSSFirstWakeBeat AcceptedBeat = Story->GetCurrentBeat();
    const bool bContactAccepted =
        AcceptedBeat == ETSTSSFirstWakeBeat::SeaContact ||
        AcceptedBeat == ETSTSSFirstWakeBeat::FlotationConfirmed;
    if (bContactAccepted && bTouchingWater && IsValid(VisualShip) &&
        VisualShip->GetCurrentForm() == EAureateWakeForm::Skyborne &&
        !VisualShip->IsTransitioning())
    {
        VisualShip->RequestForm(EAureateWakeForm::Seaborne);
    }
}
