#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TSTSSWaterLandingGate.h"
#include "TSTSSWaterContactAdapter.generated.h"

// Prototype observer: a physics-enabled hull mesh must overlap a separately
// configured water-volume actor tagged TSTSSWaterVolume.
UCLASS()
class TOSAILTHESTARRYSKY_API ATSTSSWaterContactAdapter : public AActor
{
    GENERATED_BODY()
public:
    ATSTSSWaterContactAdapter();
    virtual void BeginPlay() override;
    virtual void Tick(float DeltaSeconds) override;

    UFUNCTION(BlueprintCallable, Category="TSTSS|Water")
    void BindStory(UTSTSSFirstWakeState* InStory);

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="TSTSS|Water")
    TObjectPtr<class UStaticMeshComponent> Hull;

protected:
    UPROPERTY(Transient) TObjectPtr<UTSTSSFirstWakeState> Story;
    UPROPERTY(Transient) TObjectPtr<UTSTSSWaterLandingGate> Gate;
    // Single-player First Wake convenience; disable for authored story ownership.
    UPROPERTY(EditAnywhere, Category="TSTSS|Water")
    bool bAutoBindPlayerStory = true;

    UPROPERTY(EditAnywhere, Category="TSTSS|Water")
    FName WaterVolumeTag = TEXT("TSTSSWaterVolume");

    // Prototype displacement approximation, configured per hull. Not final hydrodynamics.
    UPROPERTY(EditAnywhere, Category="TSTSS|Buoyancy", meta=(ClampMin="0.0"))
    float MaxBuoyantAccelerationCms2 = 1800.f;
    UPROPERTY(EditAnywhere, Category="TSTSS|Buoyancy", meta=(ClampMin="0.0"))
    float VerticalDampingPerSecond = 1.5f;
    UPROPERTY(EditAnywhere, Category="TSTSS|Buoyancy", meta=(ClampMin="1.0"))
    float HullDraftCm = 120.f;
    UPROPERTY(EditAnywhere, Category="TSTSS|Buoyancy")
    bool bEnablePrototypeBuoyancy = false;
};
