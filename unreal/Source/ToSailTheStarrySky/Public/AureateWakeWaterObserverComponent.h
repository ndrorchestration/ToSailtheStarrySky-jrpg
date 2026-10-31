#pragma once
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TSTSSWaterLandingGate.h"
#include "AureateWakeWaterObserverComponent.generated.h"

class UPrimitiveComponent;
class AAureateWakePreviewActor;

/** Opt-in observer. No simulated contact or synthetic flotation receipts. */
UCLASS(ClassGroup=(TSTSS), meta=(BlueprintSpawnableComponent))
class TOSAILTHESTARRYSKY_API UAureateWakeWaterObserverComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UAureateWakeWaterObserverComponent();
    virtual void BeginPlay() override;
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* Function) override;

    /** Fail closed by default: no second story water observer runs on spawn.
     * Enable only for an isolated scene after verifying a single authoritative
     * landing observation pathway. This is NOT automatic mutual exclusion.
     */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Water")
    bool bEnableStoryWaterObservation = false;

    /** These must be scene-authored components with real overlap/collision enabled. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Water")
    TObjectPtr<UPrimitiveComponent> PhysicalHull;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Water")
    TObjectPtr<UPrimitiveComponent> WaterCollision;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Water")
    TObjectPtr<AAureateWakePreviewActor> VisualShip;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Aureate Wake|Water")
    TObjectPtr<UTSTSSFirstWakeState> Story;

private:
    UPROPERTY(Transient)
    TObjectPtr<UTSTSSWaterLandingGate> LandingGate;
};
