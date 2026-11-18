#include "TSTSSWaterContactAdapter.h"
#include "Components/StaticMeshComponent.h"
#include "TSTSSExplorerCharacter.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

#if WITH_EDITOR
#include "HAL/IConsoleManager.h"
namespace
{
// Explicitly opt in only while running the protected native review PIE.
// Defaults OFF; the bounded log is not a new physics or story authority.
TAutoConsoleVariable<int32> CVarTstssWaterReviewTrace(
    TEXT("tstss.FirstWake.WaterTrace"), 0,
    TEXT("Record bounded First Wake greybox hull/water review samples in PIE (default off)."),
    ECVF_Default);
}
#endif

ATSTSSWaterContactAdapter::ATSTSSWaterContactAdapter()
{
    PrimaryActorTick.bCanEverTick = true;
    Hull = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Hull"));
    RootComponent = Hull;
    Hull->SetGenerateOverlapEvents(true);
}

void ATSTSSWaterContactAdapter::BeginPlay()
{
    Super::BeginPlay();
    Gate = NewObject<UTSTSSWaterLandingGate>(this);
    if (bArmPrototypePhysicsOnLaunch && IsValid(Hull))
    {
        // The separate greybox does not drop its provisional hull before
        // the player actually authorizes launch. Production maps opt out.
        InitialPrototypeHullTransform = Hull->GetComponentTransform();
        bHasPrototypeInitialTransform = true;
        Hull->SetSimulatePhysics(false);
    }
    if (bAutoBindPlayerStory)
    {
        if (ATSTSSExplorerCharacter* Player = Cast<ATSTSSExplorerCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0)))
        {
            BindStory(Player->GetFirstWakeState());
        }
    }
}

void ATSTSSWaterContactAdapter::BindStory(UTSTSSFirstWakeState* InStory)
{
    Story = InStory;
    if (Gate) Gate->Reset();
}

void ATSTSSWaterContactAdapter::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!IsValid(Gate)) return;
    // Reconcile possession on every frame: respawn/repossess must not leave a
    // stale story object driving ship-water progression.
    if (bAutoBindPlayerStory)
    {
        UTSTSSFirstWakeState* CurrentPlayerStory = nullptr;
        if (ATSTSSExplorerCharacter* Player = Cast<ATSTSSExplorerCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0)))
        {
            CurrentPlayerStory = Player->GetFirstWakeState();
        }
        if (Story != CurrentPlayerStory)
        {
            BindStory(CurrentPlayerStory);
        }
    }
    if (bArmPrototypePhysicsOnLaunch)
    {
        // Review-only chronology: no prelaunch water contact is reusable as
        // proof of a later splashdown, even if the proto hull overlaps water.
        if (!IsValid(Hull) || !bHasPrototypeInitialTransform)
        {
            Gate->Reset();
            return;
        }
        const bool bStoryStarted = IsValid(Story) && Story->HasStarted();
        const bool bAfterLaunch = bStoryStarted &&
            static_cast<uint8>(Story->GetCurrentBeat()) >=
                static_cast<uint8>(ETSTSSFirstWakeBeat::Launched);
        const uint64 Generation = bStoryStarted ? Story->GetRestoreGeneration() : 0;
        const bool bNewTimeline = !bPrototypeTimelineObserved ||
            PrototypeObservedStory.Get() != Story ||
            PrototypeRestoreGeneration != Generation;
        if (bNewTimeline || !bAfterLaunch)
        {
            // On a story reset/quickload, return to the initial DRY pose.
            // The original hull physics actor cannot carry old contact into
            // a fresh timeline. No canonical ship geometry is changed.
            if (Hull->IsSimulatingPhysics())
            {
                Hull->SetSimulatePhysics(false);
            }
            Hull->SetWorldTransform(InitialPrototypeHullTransform, false, nullptr,
                                    ETeleportType::TeleportPhysics);
            Gate->Reset();
            PrototypeObservedStory = Story;
            PrototypeRestoreGeneration = Generation;
            bPrototypeTimelineObserved = true;
            if (!bAfterLaunch)
            {
#if WITH_EDITOR
                // One genuine DRY/disabled-physics sample per world second
                // (maximum 30) on the opt-in disposable PIE actor.
                UWorld* TraceWorld = GetWorld();
                if (TraceWorld && TraceWorld->WorldType == EWorldType::PIE &&
                    CVarTstssWaterReviewTrace.GetValueOnGameThread() != 0 &&
                    DryReviewTraceSamples < 30)
                {
                    const float Now = TraceWorld->GetTimeSeconds();
                    if (Now - LastDryReviewTraceWorldSeconds >= 1.f)
                    {
                        UE_LOG(LogTemp, Display,
                            TEXT("TSTSS_WATER_REVIEW_SAMPLE phase=DRY world_sec=%.4f started=%d beat=%d sim=%d hull_z_cm=%.3f stable_sec=%.4f restore_gen=%llu"),
                            Now, bStoryStarted ? 1 : 0,
                            IsValid(Story) ? static_cast<int32>(Story->GetCurrentBeat()) : -1,
                            Hull->IsSimulatingPhysics() ? 1 : 0,
                            Hull->GetComponentLocation().Z,
                            Gate->GetStableContactSeconds(),
                            static_cast<unsigned long long>(Generation));
                        LastDryReviewTraceWorldSeconds = Now;
                        ++DryReviewTraceSamples;
                    }
                }
#endif
                return;
            }
        }
        // Launch begins actual gravity/contact. Merely reaching Launched
        // does not grant SeaContact or FlotationConfirmed.
        if (!Hull->IsSimulatingPhysics())
        {
            Hull->SetSimulatePhysics(true);
        }
    }
    if (!IsValid(Story) || !IsValid(Hull) || !Hull->IsSimulatingPhysics())
    {
        Gate->Reset();
        return;
    }
    // Avoid repeated water queries after the relevant story event unless buoyancy is active.
    const ETSTSSFirstWakeBeat Beat = Story->GetCurrentBeat();
    if (!bEnablePrototypeBuoyancy && Beat != ETSTSSFirstWakeBeat::Launched &&
        Beat != ETSTSSFirstWakeBeat::SeaContact)
    {
        Gate->Reset();
        return;
    }
    TArray<AActor*> Overlaps;
    Hull->GetOverlappingActors(Overlaps, AActor::StaticClass());
    bool bInWater = false;
    float WaterSurfaceZ = -TNumericLimits<float>::Max();
    for (const AActor* Other : Overlaps)
    {
        if (IsValid(Other) && Other != this && Other->ActorHasTag(WaterVolumeTag))
        {
            // Only bounded water volumes with valid world-space bounds count.
            FVector Origin, Extent;
            Other->GetActorBounds(false, Origin, Extent);
            if (FMath::IsFinite(Origin.Z) && FMath::IsFinite(Extent.Z) && Extent.Z > 0.f)
            {
                bInWater = true;
                WaterSurfaceZ = FMath::Max(WaterSurfaceZ, Origin.Z + Extent.Z);
            }
        }
    }
    // UE 5.8 exposes current world-space component bounds through GetBounds().
    const FBoxSphereBounds HullBounds = Hull->GetBounds();
    const FVector HullOrigin = HullBounds.Origin;
    const FVector HullExtent = HullBounds.BoxExtent;
    // Invalid authored configuration must never generate buoyancy or landing proof.
    if (!FMath::IsFinite(HullDraftCm) || HullDraftCm <= 1.f ||
        !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.f)
    {
        Gate->Reset();
        return;
    }
    if (!FMath::IsFinite(HullOrigin.Z) || !FMath::IsFinite(HullExtent.Z) ||
        HullExtent.Z <= 0.f)
    {
        Gate->Reset();
        return;
    }
    const float Draft = HullDraftCm;
    const float Submersion = bInWater && FMath::IsFinite(WaterSurfaceZ)
        ? FMath::Clamp((WaterSurfaceZ - (HullOrigin.Z - Draft)) / (2.f * Draft), 0.f, 1.f)
        : 0.f;
    // Mere overlap with a tagged volume is not sufficient for sea contact.
    // Require the hull's lower bound to be below the authored surface, not
    // merely an overlapping volume's broad bounding box.
    const bool bBelowSurface = bInWater &&
        (HullOrigin.Z - HullExtent.Z) < WaterSurfaceZ;
    const bool bActualImmersion = bBelowSurface && Submersion > 0.01f;
    const float VerticalSpeed = Hull->GetPhysicsLinearVelocity().Z;
    if (!FMath::IsFinite(VerticalSpeed) || !FMath::IsFinite(Submersion))
    {
        Gate->Reset();
        return;
    }
    if (bActualImmersion && bEnablePrototypeBuoyancy && HullDraftCm > 1.f &&
        FMath::IsFinite(MaxBuoyantAccelerationCms2) &&
        FMath::IsFinite(VerticalDampingPerSecond) &&
        FMath::IsFinite(WaterSurfaceZ))
    {
        // Bound net force to avoid runaway impulses from invalid tuning.
        const float MaxAcceleration = FMath::Clamp(MaxBuoyantAccelerationCms2, 0.f, 4000.f);
        const float Damping = FMath::Clamp(VerticalDampingPerSecond, 0.f, 10.f);
        const float Acceleration = FMath::Clamp(MaxAcceleration * Submersion -
            Damping * VerticalSpeed, -MaxAcceleration, MaxAcceleration);
        const float Mass = Hull->GetMass();
        if (Mass > 0.f && FMath::IsFinite(Acceleration))
        {
            Hull->AddForce(FVector(0.f, 0.f, Mass * Acceleration));
        }
    }
#if WITH_EDITOR
    const ETSTSSFirstWakeBeat BeforeObservedBeat = Story->GetCurrentBeat();
#endif
    Gate->Observe(DeltaSeconds, bActualImmersion, VerticalSpeed, Story);

#if WITH_EDITOR
    // Per-physics-frame values: direct measurements, not inferred from HUD
    // objectives. Explicitly opt in; bound one actor to 6000 finite samples.
    // Logging NEVER changes collision, forces, state or save content.
    UWorld* TraceWorld = GetWorld();
    if (bArmPrototypePhysicsOnLaunch && TraceWorld &&
        TraceWorld->WorldType == EWorldType::PIE &&
        CVarTstssWaterReviewTrace.GetValueOnGameThread() != 0 &&
        PhysicalReviewTraceSamples < 6000)
    {
        UE_LOG(LogTemp, Display,
            TEXT("TSTSS_WATER_REVIEW_SAMPLE phase=PHYSICS world_sec=%.4f dt=%.4f hull_z_cm=%.3f hull_bottom_z_cm=%.3f water_surface_z_cm=%.3f tagged_overlap=%d immersed=%d submersion=%.5f vertical_speed_cm_s=%.3f stable_sec=%.4f beat_before=%d beat_after=%d sim=%d restore_gen=%llu"),
            TraceWorld->GetTimeSeconds(), DeltaSeconds, HullOrigin.Z,
            HullOrigin.Z - HullExtent.Z, WaterSurfaceZ,
            bInWater ? 1 : 0, bActualImmersion ? 1 : 0,
            Submersion, VerticalSpeed, Gate->GetStableContactSeconds(),
            static_cast<int32>(BeforeObservedBeat),
            static_cast<int32>(Story->GetCurrentBeat()),
            Hull->IsSimulatingPhysics() ? 1 : 0,
            static_cast<unsigned long long>(Story->GetRestoreGeneration()));
        ++PhysicalReviewTraceSamples;
    }
#endif
}
