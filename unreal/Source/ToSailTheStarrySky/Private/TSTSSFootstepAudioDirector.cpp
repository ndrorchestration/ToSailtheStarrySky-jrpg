#include "TSTSSFootstepAudioDirector.h"

#include "TSTSSAudioSubsystem.h"

#include "CollisionQueryParams.h"
#include "Engine/World.h"
#include "GameFramework/Character.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Pawn.h"
#include "Kismet/GameplayStatics.h"
#include "PhysicalMaterials/PhysicalMaterial.h"

ATSTSSFootstepAudioDirector::ATSTSSFootstepAudioDirector()
{
    PrimaryActorTick.bCanEverTick = true;
    SetActorEnableCollision(false);
}

void ATSTSSFootstepAudioDirector::BeginPlay()
{
    Super::BeginPlay();
    ResetFootstepTracking();
}

void ATSTSSFootstepAudioDirector::ResetFootstepTracking()
{
    TrackedPawn.Reset();
    LastGroundLocation = FVector::ZeroVector;
    DistanceAccumulatorCm = 0.0f;
    bHasLastGroundLocation = false;
}

FName ATSTSSFootstepAudioDirector::CueForSurface(
    EPhysicalSurface Surface, EPhysicalSurface Wood, EPhysicalSurface Sand,
    EPhysicalSurface Stone, EPhysicalSurface Metal)
{
    if (Surface == Wood) return FName(TEXT("foley.footstep.wood"));
    if (Surface == Sand) return FName(TEXT("foley.footstep.sand"));
    if (Surface == Stone) return FName(TEXT("foley.footstep.stone"));
    if (Surface == Metal) return FName(TEXT("foley.footstep.metal"));
    return NAME_None; // Default/unknown material: no invented surface classification.
}

void ATSTSSFootstepAudioDirector::Tick(float DeltaSeconds)
{
    Super::Tick(DeltaSeconds);
    if (!bEnabled || !FMath::IsFinite(DeltaSeconds) || DeltaSeconds <= 0.0f)
    {
        ResetFootstepTracking();
        return;
    }

    UWorld* World = GetWorld();
    APawn* Pawn = World ? UGameplayStatics::GetPlayerPawn(World, 0) : nullptr;
    ACharacter* Character = Cast<ACharacter>(Pawn);
    UCharacterMovementComponent* Movement = IsValid(Character)
        ? Character->GetCharacterMovement() : nullptr;
    if (!IsValid(Pawn) || !IsValid(Movement) || !Movement->IsMovingOnGround())
    {
        ResetFootstepTracking();
        return; // No sounds in air, water, menu, or pawn-less levels.
    }

    const FVector Position = Pawn->GetActorLocation();
    if (TrackedPawn.Get() != Pawn || !bHasLastGroundLocation)
    {
        TrackedPawn = Pawn;
        LastGroundLocation = Position;
        DistanceAccumulatorCm = 0.0f;
        bHasLastGroundLocation = true;
        return;
    }
    const float TravelCm = FVector::Dist2D(Position, LastGroundLocation);
    LastGroundLocation = Position;

    if (!FMath::IsFinite(TravelCm) || TravelCm > MaximumContinuityDeltaCm)
    {
        DistanceAccumulatorCm = 0.0f;
        return; // Quicksave/teleport or discontinuity; never generate a step burst.
    }
    const FVector Velocity = Pawn->GetVelocity();
    if (Velocity.Size2D() < MinimumGroundSpeedCmPerSec)
    {
        DistanceAccumulatorCm = 0.0f;
        return; // Standing still, even when input buttons are pressed.
    }
    DistanceAccumulatorCm += TravelCm;
    if (DistanceAccumulatorCm < StepDistanceCm) return;
    DistanceAccumulatorCm = FMath::Fmod(DistanceAccumulatorCm, StepDistanceCm);

    FCollisionQueryParams Params(SCENE_QUERY_STAT(TSTSSGroundFootstep), false, Pawn);
    Params.bReturnPhysicalMaterial = true;
    FHitResult Hit;
    const FVector TraceEnd = Position - FVector(0.f, 0.f, 250.f);
    if (!World->LineTraceSingleByChannel(Hit, Position, TraceEnd, ECC_Visibility, Params))
        return;

    const EPhysicalSurface Surface =
        UPhysicalMaterial::DetermineSurfaceType(Hit.PhysMaterial.Get());
    const FName Event = CueForSurface(
        Surface, WoodSurface.GetValue(), SandSurface.GetValue(),
        StoneSurface.GetValue(), MetalSurface.GetValue());
    if (Event.IsNone()) return;

    if (UTSTSSAudioSubsystem* Audio = World->GetSubsystem<UTSTSSAudioSubsystem>())
    {
        Audio->EmitCue(Event, Hit.ImpactPoint);
    }
}
