#pragma once

#include "CoreMinimal.h"
#include "Engine/EngineTypes.h"
#include "GameFramework/Actor.h"
#include "TSTSSFootstepAudioDirector.generated.h"

class APawn;

/**
 * Optional player-only acoustic observer. Read-only ground trace and physical
 * material dispatch; no input bindings, movement modifications or story writes.
 * Place one in the review level and register its cue IDs in the sound bank.
 */
UCLASS(Blueprintable)
class TOSAILTHESTARRYSKY_API ATSTSSFootstepAudioDirector : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSFootstepAudioDirector();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps")
    bool bEnabled = true;

    /** Horizontal distance per step; not a cadence timer. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps",
              meta=(ClampMin="35.0", ClampMax="220.0"))
    float StepDistanceCm = 105.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps",
              meta=(ClampMin="1.0", ClampMax="200.0"))
    float MinimumGroundSpeedCmPerSec = 35.0f;

    /** Prevent fast position jumps from emitting a burst of fake footsteps. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps",
              meta=(ClampMin="110.0", ClampMax="1000.0"))
    float MaximumContinuityDeltaCm = 220.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps|PhysicalSurfaces")
    TEnumAsByte<EPhysicalSurface> WoodSurface = SurfaceType1;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps|PhysicalSurfaces")
    TEnumAsByte<EPhysicalSurface> SandSurface = SurfaceType2;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps|PhysicalSurfaces")
    TEnumAsByte<EPhysicalSurface> StoneSurface = SurfaceType3;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="TSTSS|Audio|Footsteps|PhysicalSurfaces")
    TEnumAsByte<EPhysicalSurface> MetalSurface = SurfaceType4;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Audio|Footsteps")
    void ResetFootstepTracking();

private:
    UPROPERTY(Transient)
    TWeakObjectPtr<APawn> TrackedPawn;

    FVector LastGroundLocation = FVector::ZeroVector;
    float DistanceAccumulatorCm = 0.0f;
    bool bHasLastGroundLocation = false;

    static FName CueForSurface(EPhysicalSurface Surface,
                              EPhysicalSurface Wood,
                              EPhysicalSurface Sand,
                              EPhysicalSurface Stone,
                              EPhysicalSurface Metal);
};
