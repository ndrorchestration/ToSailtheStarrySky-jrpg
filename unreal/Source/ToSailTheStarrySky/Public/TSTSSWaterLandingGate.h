#pragma once
#include "CoreMinimal.h"
#include "UObject/Object.h"
#include "TSTSSFirstWakeState.h"
#include "TSTSSWaterLandingGate.generated.h"

// Physics observations must originate in a real ship/water collision component.
// This logic gate does not itself simulate waves, hull buoyancy or water overlaps.
UCLASS(BlueprintType)
class TOSAILTHESTARRYSKY_API UTSTSSWaterLandingGate : public UObject
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, Category="TSTSS|Water")
    bool Observe(float DeltaSeconds, bool bHullTouchesWater, float HullVerticalSpeedCms, UTSTSSFirstWakeState* Story);

    UFUNCTION(BlueprintCallable, Category="TSTSS|Water")
    void Reset()
    {
        StableContactSeconds = 0.f;
        bContactRecorded = false;
        bHasPreviousStableSample = false;
        ObservedRestoreGeneration = 0;
        bHasObservedRestoreGeneration = false;
    }

    UFUNCTION(BlueprintPure, Category="TSTSS|Water")
    float GetStableContactSeconds() const { return StableContactSeconds; }

private:
    UPROPERTY() float StableContactSeconds = 0.f;
    UPROPERTY() bool bContactRecorded = false;
    // First qualifying sample anchors the clock; the prior interval is unobserved.
    UPROPERTY(Transient) bool bHasPreviousStableSample = false;
    UPROPERTY(Transient) uint64 ObservedRestoreGeneration = 0;
    UPROPERTY(Transient) bool bHasObservedRestoreGeneration = false;
};
